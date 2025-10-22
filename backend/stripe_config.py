import os
import threading
import time  # For startup delay
import stripe
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from firebase_admin import db  # For Firebase updates

load_dotenv()  # MUST be at top to load .env immediately

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
if not stripe.api_key:
    logging.error("STRIPE_SECRET_KEY missing in .env")
    raise ValueError("STRIPE_SECRET_KEY not set")

endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
if not endpoint_secret:
    logging.warning("STRIPE_WEBHOOK_SECRET missing (webhooks may fail)")

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Server running'})

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json()
        if not data:
            logging.error("No JSON payload received")
            return jsonify({'error': 'No JSON data provided'}), 400

        user_id = data.get('user_id')
        price_id = data.get('price_id')
        if not user_id or not price_id:
            logging.error(f"Missing fields: user_id={user_id}, price_id={price_id}")
            return jsonify({'error': 'Missing user_id or price_id'}), 400

        logging.info(f"Creating Checkout Session for user {user_id} with price {price_id}")
        
        # Create session with explicit error handling
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='payment',
            success_url=f"{request.host_url}success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url}cancel",
            client_reference_id=user_id,
            metadata={'user_id': user_id}
        )
        logging.info(f"Session created: {session.id}")
        return jsonify({'url': session.url})

    except stripe.error.InvalidRequestError as e:
        error_msg = f"Invalid request: {e.user_message or str(e)}"
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 400
    except stripe.error.AuthenticationError as e:
        error_msg = "Stripe authentication failed (bad API key)"
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 401
    except stripe.error.APIConnectionError as e:
        error_msg = "Network error connecting to Stripe"
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/success')
def success():
    logging.info("Success page accessed")
    # HTML with meta refresh to close tab after 3s
    return """
    <html>
        <head>
            <title>Payment Successful</title>
            <meta http-equiv="refresh" content="3;url=about:blank" />  <!-- Auto-close -->
            <style>body { font-family: Arial; text-align: center; margin-top: 50px; }</style>
        </head>
        <body>
            <h1>Payment successful!</h1>
            <p>Premium unlocked. This tab will close automatically. Return to the game.</p>
        </body>
    </html>
    """

@app.route('/cancel')
def cancel():
    logging.info("Cancel page accessed")
    return "Payment cancelled. Close this tab and try again."

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        logging.info(f"Webhook event received: {event['type']}")
    except ValueError as e:
        logging.error(f"Invalid payload: {e}")
        return '', 400
    except stripe.error.SignatureVerificationError as e:
        logging.error(f"Invalid signature: {e}")
        return '', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['client_reference_id']
        if session['payment_status'] == 'paid':
            logging.info(f"Unlocking premium for user {user_id}")
            user_ref = db.reference(f'users/{user_id}')
            user_ref.update({'onetime_payment_made': True})
            
    return '', 200

def run_server(port=3000):
    logging.info(f"Starting Flask server on http://127.0.0.1:{port}")
    app.run(port=port, debug=True, use_reloader=False)

def start_background_server(port=3000):
    thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    thread.start()
    time.sleep(2)  # Wait 2s for server to bind port
    logging.info("Flask background thread started and ready")
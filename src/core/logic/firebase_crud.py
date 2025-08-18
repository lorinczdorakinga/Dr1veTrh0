from firebase_admin import db
from typing import Dict, List, Optional, Any
import pyrebase
import os
import json
from firebase_admin import credentials, auth, db
from dotenv import load_dotenv
from src.components.notification import show_notification

class FirebaseCRUD:
    def __init__(self):
        load_dotenv()
        self.cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        self.db_url = os.getenv('FIREBASE_DATABASE_URL')
        required_vars = {
            "FIREBASE_CREDENTIALS_PATH": self.cred_path,
            "FIREBASE_DATABASE_URL": self.db_url,
            "FIREBASE_API_KEY": os.getenv('FIREBASE_API_KEY'),
            "FIREBASE_AUTH_DOMAIN": os.getenv('FIREBASE_AUTH_DOMAIN'),
            "FIREBASE_STORAGE_BUCKET": os.getenv('FIREBASE_STORAGE_BUCKET'),
            "FIREBASE_MESSAGING_SENDER_ID": os.getenv('MESSAGING_SENDER_ID'),
            "FIREBASE_APP_ID": os.getenv('APP_ID')
        }
        missing_vars = [key for key, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

        self.ref = db.reference("/users")
        
        self.client_config = {
            "apiKey": os.getenv('FIREBASE_API_KEY'),
            "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
            "databaseURL": self.db_url,
            "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
            "messagingSenderId": os.getenv('MESSAGING_SENDER_ID'),
            "appId": os.getenv('APP_ID'),
        }
        
        self.firebase_client = pyrebase.initialize_app(self.client_config)
        self.client_auth = self.firebase_client.auth()

    def create_user(self, username, email, password):
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            user_ref = db.reference(f'users/{user.uid}')
            user_ref.set({
                'username': username,
                'email': email,
                'default_mode_highscore': 0,
                'reverse_mode_highscore': 0,
                'speedrun_mode_highscore': 0,
                'double_trouble_mode_highscore': 0
            })
            return user
        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                show_notification("Error", "A user with this email already exists.")
            elif "INVALID_EMAIL" in error_message:
                show_notification("Error", "Invalid email format.")
            elif "WEAK_PASSWORD" in error_message:
                show_notification("Error", "Password is too weak. Must be at least 6 characters.")
            else:
                show_notification("Error", f"Failed to create user: {error_message}")
            print(f"Error creating user: {error_message}")
            return None

    def register_user(self, username, email, password):
        if not username:
            show_notification("Error", "Username is required.")
            return None
        return self.create_user(username, email, password)

    def login_user(self, email, password):
        try:
            user = self.client_auth.sign_in_with_email_and_password(email, password)
            return user
        except Exception as e:
            try:
                error_json = e.args[1]
                error = json.loads(error_json)['error']['message']
            except (IndexError, json.JSONDecodeError):
                error = str(e)
            if error == "INVALID_PASSWORD":
                show_notification("Error", "Invalid password.")
            elif error == "EMAIL_NOT_FOUND":
                show_notification("Error", "Email not found.")
            elif error == "USER_DISABLED":
                show_notification("Error", "This account has been disabled.")
            else:
                show_notification("Error", f"Login failed: {error}")
            print(f"Login error: {error}")
            return None

    def refresh_user(self, refresh_token):
        try:
            refreshed_user = self.client_auth.refresh(refresh_token)
            return refreshed_user
        except Exception as e:
            error_str = str(e)
            if "TOKEN_EXPIRED" in error_str or "INVALID_REFRESH_TOKEN" in error_str:
                print("Refresh token expired. User needs to log in again.")
                return "TOKEN_EXPIRED"
            else:
                print(f"Refresh failed: {e}")
                return None
        
    def reauthenticate_user(self, email, password):
        try:
            user = self.client_auth.sign_in_with_email_and_password(email, password)
            return user
        except Exception as e:
            print(f"Re-authentication failed: {e}")
            show_notification("Error", f"Re-authentication failed: {str(e)}")
            return None

    def get_account_info(self, id_token):
        try:
            return self.client_auth.get_account_info(id_token)
        except pyrebase.exceptions.HTTPError as e:
            try:
                error_json = e.args[1]
                error = json.loads(error_json)['error']['message']
            except (IndexError, json.JSONDecodeError):
                error = str(e)
            print(f"Failed to get account info: {error}")
            show_notification("Error", f"Failed to get account info: {error}")
            return None
        except Exception as e:
            print(f"Failed to get account info: {e}")
            show_notification("Error", f"Failed to get account info: {str(e)}")
            return None

    def search_by_username(self, username):
        try:
            users = self.ref.order_by_child("username").equal_to(username).get()
            return users
        except Exception as e:
            print(f"Error searching by username: {e}")
            show_notification("Error", f"Failed to search users: {str(e)}")
            return None

    def recover_password_by_email(self, email):
        try:
            self.client_auth.send_password_reset_email(email)
            show_notification("Success", "Password reset email sent.")
            return True
        except Exception as e:
            print(f"Error sending password reset email: {e}")
            show_notification("Error", f"Failed to send password reset email: {str(e)}")
            return False
        
    def send_email_verification(self, id_token):
        import requests
        api_key = self.client_config['apiKey']
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token
        }
        
        try:
            response = requests.post(url, json=payload)
            result = response.json()
            
            if response.status_code == 200:
                show_notification("Success", "Verification email sent.")
                return True
            else:
                error_message = result.get('error', {}).get('message', 'Unknown error')
                print(f"Email verification error: {error_message}")
                show_notification("Error", f"Email verification failed: {error_message}")
                return False
        except Exception as e:
            print(f"Request error: {str(e)}")
            show_notification("Error", f"Request error: {str(e)}")
            return False
        
    def get_user_highscore_by_mode(self, uid, game_mode):
        try:
            user_ref = db.reference(f'users/{uid}')
            user_data = user_ref.get()
            if user_data:
                highscore_key = f'{game_mode}_mode_highscore'
                highscore = user_data.get(highscore_key, 0)
                print(f"Fetched highscore for {game_mode}: {highscore}")
                return highscore
            print(f"No user data found for UID: {uid}")
            return 0
        except Exception as e:
            print(f"Error getting user highscore: {e}")
            show_notification("Error", f"Failed to fetch highscore: {str(e)}")
            return 0

    def update_highscore(self, uid, game_mode, score):
        try:
            user_ref = db.reference(f'users/{uid}')
            current_data = user_ref.get()
            highscore_key = f'{game_mode}_mode_highscore'
            current_score = current_data.get(highscore_key, 0) if current_data else 0
            if score > current_score:
                user_ref.update({highscore_key: score})
                print(f"Updated {game_mode} highscore for user {uid}: {score}")
        except Exception as e:
            print(f"Error updating highscore: {e}")
            show_notification("Error", f"Failed to update highscore: {str(e)}")

    def update_user_email(self, id_token, new_email):
        import requests
        api_key = self.client_config['apiKey']
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
        payload = {"idToken": id_token, "email": new_email, "returnSecureToken": True}
        
        try:
            response = requests.post(url, json=payload)
            result = response.json()
            
            if response.status_code == 200:
                show_notification("Success", "Email updated successfully.")
                return result
            else:
                error_message = result.get('error', {}).get('message', 'Unknown error')
                print(f"Firebase error: {error_message}")
                show_notification("Error", f"Failed to update email: {error_message}")
                return None
        except Exception as e:
            print(f"Request error: {str(e)}")
            show_notification("Error", f"Request error: {str(e)}")
            return None

    def update_user_password(self, id_token, new_password):
        import requests
        api_key = self.client_config['apiKey']
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
        payload = {"idToken": id_token, "password": new_password, "returnSecureToken": True}
        
        try:
            response = requests.post(url, json=payload)
            result = response.json()
            
            if response.status_code == 200:
                show_notification("Success", "Password updated successfully.")
                return result
            else:
                error_message = result.get('error', {}).get('message', 'Unknown error')
                print(f"Firebase error: {error_message}")
                show_notification("Error", f"Failed to update password: {error_message}")
                return None
        except Exception as e:
            print(f"Request error: {str(e)}")
            show_notification("Error", f"Request error: {str(e)}")
            return None

    def get_user_records(self, uid):
        try:
            user_ref = db.reference(f'users/{uid}')
            records = user_ref.get()
            print(f"Fetched user records for UID {uid}: {records}")
            return records
        except Exception as e:
            print(f"Error getting user records: {e}")
            show_notification("Error", f"Failed to fetch user records: {str(e)}")
            return None
        
    def refresh_id_token(self, refresh_token):
        import requests
        api_key = self.client_config['apiKey']
        url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"Refreshed token for user: {result.get('user_id')}")
                return {
                    'idToken': result['id_token'],
                    'refreshToken': result['refresh_token']
                }
            else:
                error_message = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"Token refresh error: {error_message}")
                return None
        except Exception as e:
            print(f"Token refresh error: {str(e)}")
            show_notification("Error", f"Token refresh failed: {str(e)}")
            return None
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
                print("A user with this email already exists.")
            elif "INVALID_EMAIL" in error_message:
                print("Invalid email format.")
            elif "WEAK_PASSWORD" in error_message:
                print("Password is too weak.")
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
        except Exception as error:
            # error_json = e.args[1]
            # error = json.loads(error_json)['error']['message']
            if error == "INVALID_PASSWORD":
                return "Invalid password."
            elif error == "EMAIL_NOT_FOUND":
                return "Email not found."
            elif error == "USER_DISABLED":
                return "This account has been disabled."
            else:
                return f"Login failed: {str(error)}"


    def refresh_user(self, refresh_token):
        try:
            return self.client_auth.refresh(refresh_token)
        except Exception as e:
            print(f"Refresh failed: {e}")
            return None

    def get_account_info(self, id_token):
        try:
            return self.client_auth.get_account_info(id_token)
        except pyrebase.exceptions.HTTPError as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            print(f"Failed to get account info: {error}")
            return None
        except Exception as e:
            print(f"Failed to get account info: {e}")
            return None
    def search_by_username(self, username):
        try:
            users = self.ref.order_by_child("username").equal_to(username).get()
            return users
        except Exception as e:
            return None

    def recover_password_by_email(self, email):
        try:
            self.client_auth.send_password_reset_email(email)
            return True
        except Exception as e:
            return False

    def update_highscore(self, uid, game_mode, score, email):
        try:
            user = auth.get_user_by_email(email)
            user_ref = db.reference(f'users/{user.uid}')
            current_data = user_ref.get()
            current_score = current_data.get(f'{game_mode}_highscore', 0)
            if score > current_score:
                user_ref.update({f'{game_mode}_highscore': score})
                print(f"Updated {game_mode} highscore for user {uid}: {score}")
        except Exception as e:
            print(f"Error updating highscore: {e}")

    def update_user_email(self, id_token, new_email):
        import requests
        api_key = self.client_config['apiKey']
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
        payload = {"idToken": id_token, "email": new_email, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        return response.json() if response.status_code == 200 else None

    def update_user_password(self, id_token, new_password):
        import requests
        api_key = self.client_config['apiKey']
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
        payload = {"idToken": id_token, "password": new_password, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        return response.json() if response.status_code == 200 else None

    def get_user_records(self, uid):
        try:
            user_ref = db.reference(f'users/{uid}')
            return user_ref.get()
        except Exception as e:
            print(f"Error getting user records: {e}")
            return None
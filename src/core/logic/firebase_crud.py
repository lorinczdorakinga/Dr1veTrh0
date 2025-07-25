from firebase_admin import db
from typing import Dict, List, Optional, Any

from backend.firebase_exceptions import handle_firebase_error
import time
import os
from firebase_admin import credentials, auth, db
import uuid
from dotenv import load_dotenv

class FirebaseCRUD:
    def __init__(self):
        load_dotenv()
        self.cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        self.db_url = os.getenv('FIREBASE_DATABASE_URL')
        self.ref = db.reference("/users")

    def create_user(self, email, password, username):
        try:
            # Create user in Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username  # Optional: Store username in Firebase Auth
            )
            # Store user data in Realtime Database
            user_ref = db.reference(f'users/{user.uid}')
            user_ref.set({
                'username': username,
                'email': email,
                'password': password,
                'default_mode_highscore': 0,
                'reverse_mode_highscore': 0,
                'speedrun_mode_highscore': 0,
                'double_trouble_mode_highscore': 0
            })
            print(f"User created with UID: {user.uid}")
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            return None, None
        
    def register_user(self, email, password, username):
        if not username:
            print("Registration Failed", "Username is required.")
            return
        user = self.create_user(email, password, username)

    def login_user(self, username_or_email, password):
        if '@' in username_or_email and '.' in username_or_email:
            try:
                # Verify user by email
                user = auth.get_user_by_email(username_or_email)
                user_ref = db.reference(f'users/{user.uid}')
                user_data = user_ref.get()
                print(f"Login successful for user: {user.email}")
                return user
            except Exception as e:
                print(f"Error logging in with email: {e}")
                return None
        else:
            try:
                # Verify user by username
                users = self.search_by_username(username_or_email)
                if users is None or len(users) == 0:
                    print("User not found.")
                    return None
                
                user = list(users.values())[0]  # Get the first user from the dictionary
                user_uid = user.get('uid')  # Extract uid from the user dictionary
                user_ref = db.reference(f'users/{user_uid}')
                user_data = user_ref.get()
                print(f"Login successful for user: {user.get('username')}")  # Access username using dictionary key
                return user
            except Exception as e:
                print(f"Error logging in with username: {e}")
                return None

    def search_by_username(self, username):
        try:
            users = self.ref.order_by_child("username").equal_to(username).get()
            return users  # Return the raw users dictionary
        except Exception as e:
            print(f"Error searching by username: {e}")
            return None

        
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





   
    
    # CREATE Operations
    def create(self, data: Dict[str, Any], custom_id: Optional[str] = None) -> str:
        """
        Create a new record in Firebase
        
        Args:
            data: Dictionary containing the data to store
            custom_id: Optional custom ID, if not provided Firebase generates one
            
        Returns:
            The ID of the created record
        """
        try:
            if custom_id:
                self.ref.child(custom_id).set(data)
                return custom_id
            else:
                new_ref = self.ref.push(data)
                return new_ref.key
                
        except Exception as e:
            print(f"Error creating record: {e}")
            raise e
    
    def create_multiple(self, data_list: List[Dict[str, Any]]) -> List[str]:
        """
        Create multiple records at once
        
        Args:
            data_list: List of dictionaries to store
            
        Returns:
            List of created record IDs
        """
        created_ids = []
        try:
            for data in data_list:
                record_id = self.create(data)
                created_ids.append(record_id)
            return created_ids
            
        except Exception as e:
            print(f"Error creating multiple records: {e}")
            raise e
    
    # READ Operations
    def read(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a single record by ID
        
        Args:
            record_id: ID of the record to retrieve
            
        Returns:
            Dictionary containing the record data or None if not found
        """
        try:
            data = self.ref.child(record_id).get()
            return data
            
        except Exception as e:
            print(f"Error reading record {record_id}: {e}")
            return None
    
    def read_all(self) -> Dict[str, Any]:
        """
        Read all records in the collection
        
        Returns:
            Dictionary with all records (key: record_id, value: record_data)
        """
        try:
            data = self.ref.get()
            return data if data else {}
            
        except Exception as e:
            print(f"Error reading all records: {e}")
            return {}
    
    def read_filtered(self, field: str, value: Any, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Read records filtered by field value
        
        Args:
            field: Field name to filter by
            value: Value to filter for
            limit: Optional limit on number of results
            
        Returns:
            Dictionary with filtered records
        """
        try:
            query = self.ref.order_by_child(field).equal_to(value)
            if limit:
                query = query.limit_to_first(limit)
            
            data = query.get()
            return data if data else {}
            
        except Exception as e:
            print(f"Error reading filtered records: {e}")
            return {}
    
    # UPDATE Operations
    def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a record by ID
        
        Args:
            record_id: ID of the record to update
            data: Dictionary containing fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ref.child(record_id).update(data)
            return True
            
        except Exception as e:
            print(f"Error updating record {record_id}: {e}")
            return False
    
    def update_field(self, record_id: str, field: str, value: Any) -> bool:
        """
        Update a single field in a record
        
        Args:
            record_id: ID of the record to update
            field: Field name to update
            value: New value for the field
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ref.child(record_id).child(field).set(value)
            return True
            
        except Exception as e:
            print(f"Error updating field {field} in record {record_id}: {e}")
            return False
    
    # DELETE Operations
    def delete(self, record_id: str) -> bool:
        """
        Delete a record by ID
        
        Args:
            record_id: ID of the record to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ref.child(record_id).delete()
            return True
            
        except Exception as e:
            print(f"Error deleting record {record_id}: {e}")
            return False
    
    def delete_all(self) -> bool:
        """
        Delete all records in the collection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ref.delete()
            return True
            
        except Exception as e:
            print(f"Error deleting all records: {e}")
            return False
    
    def delete_filtered(self, field: str, value: Any) -> int:
        """
        Delete records that match a filter condition
        
        Args:
            field: Field name to filter by
            value: Value to filter for
            
        Returns:
            Number of records deleted
        """
        try:
            # First, get the records to delete
            records_to_delete = self.read_filtered(field, value)
            
            if not records_to_delete:
                return 0
            
            # Delete each record
            deleted_count = 0
            for record_id in records_to_delete.keys():
                if self.delete(record_id):
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"Error deleting filtered records: {e}")
            return 0
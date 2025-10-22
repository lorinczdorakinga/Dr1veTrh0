from pathlib import Path
import sys
from firebase_admin import db
from firebase_admin import db
from .firebase_crud import FirebaseCRUD 

def get_resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent
        base_path = base_path.parent.parent  # Go up to the root of the project
    path = base_path / 'assets' / relative_path
    if not path.exists():
        print (path)
        print(f"Warning: Resource {relative_path} not found.")
        return str(base_path / "img/default.png")
    return str(path)

def did_user_pay() -> bool:
    from src.scenes.menu.auth_handler import AuthHandler
    auth_handler = AuthHandler()
    if not auth_handler.is_user_logged_in():
        return False
    
    # Get the Auth user (likely a dict from pyrebase or firebase_admin.auth.UserRecord)
    auth_user = auth_handler.get_current_user()
    if not auth_user:
        return False
    
    # Get UID (pyrebase returns 'localId', admin returns 'uid')
    uid = auth_user.get('localId') or auth_user.get('uid')
    if not uid:
        return False
    
    # Fetch user data from DB securely
    user_ref = db.reference(f'users/{uid}')
    user_data = user_ref.get()
    
    if isinstance(user_data, dict):
        # Safely get the field, default to False
        return user_data.get('onetime_payment_made', False)
    
    return False
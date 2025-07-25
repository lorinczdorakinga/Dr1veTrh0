class FirebaseError(Exception):
    """Base exception for Firebase operations"""
    pass

class FirebaseConnectionError(FirebaseError):
    """Raised when there's a connection issue with Firebase"""
    pass

class FirebaseAuthError(FirebaseError):
    """Raised when there's an authentication issue"""
    pass

class FirebaseDataError(FirebaseError):
    """Raised when there's a data validation issue"""
    pass

def handle_firebase_error(func):
    """Decorator to handle Firebase errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "auth" in str(e).lower():
                raise FirebaseAuthError(f"Authentication error: {e}")
            elif "connection" in str(e).lower() or "network" in str(e).lower():
                raise FirebaseConnectionError(f"Connection error: {e}")
            else:
                raise FirebaseError(f"Firebase operation failed: {e}")
    return wrapper
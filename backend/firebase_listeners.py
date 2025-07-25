from firebase_admin import db
from backend.firebase_config import firebase_config
import threading
from typing import Callable, Optional

class FirebaseListener:
    def __init__(self, collection_name: str = ''):
        self.collection_name = collection_name
        self.ref = firebase_config.get_database_reference(collection_name)
        self.listeners = {}
    
    def listen_to_changes(self, callback: Callable, child_path: str = '') -> str:
        """
        Listen to real-time changes in Firebase
        
        Args:
            callback: Function to call when data changes
            child_path: Optional specific child path to listen to
            
        Returns:
            Listener ID for removing the listener later
        """
        def listener(event):
            callback(event.data, event.path)
        
        if child_path:
            ref = self.ref.child(child_path)
        else:
            ref = self.ref
            
        # Add listener
        listener_id = f"listener_{len(self.listeners)}"
        ref.listen(listener)
        self.listeners[listener_id] = ref
        
        return listener_id
    
    def listen_to_child_events(self, 
                              on_child_added: Optional[Callable] = None,
                              on_child_changed: Optional[Callable] = None,
                              on_child_removed: Optional[Callable] = None) -> str:
        """
        Listen to specific child events
        
        Args:
            on_child_added: Callback for when a child is added
            on_child_changed: Callback for when a child is changed
            on_child_removed: Callback for when a child is removed
            
        Returns:
            Listener ID
        """
        def event_listener(event):
            if event.event_type == 'put' and event.path == '/':
                # Initial data load or complete replacement
                if on_child_added:
                    on_child_added(event.data, event.path)
            elif event.event_type == 'put':
                # Child added or changed
                if on_child_changed:
                    on_child_changed(event.data, event.path)
            elif event.event_type == 'patch':
                # Child updated
                if on_child_changed:
                    on_child_changed(event.data, event.path)
        
        listener_id = f"child_listener_{len(self.listeners)}"
        self.ref.listen(event_listener)
        self.listeners[listener_id] = self.ref
        
        return listener_id
    
    def remove_listener(self, listener_id: str):
        """Remove a specific listener"""
        if listener_id in self.listeners:
            # Note: firebase-admin doesn't have a direct way to remove listeners
            # You would need to keep track of the listener reference
            del self.listeners[listener_id]
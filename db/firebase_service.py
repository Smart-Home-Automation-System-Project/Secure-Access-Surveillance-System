import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
import sqlite3
from datetime import datetime
import time
import threading
from dotenv import load_dotenv

class FirebaseService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Load environment variables
        load_dotenv()
        
        # Database path
        self.db_path = './db/security.db'
        
        try:
            # Initialize Firebase
            cred = credentials.Certificate("./config/service_account_key.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
            })
            
            self.db_ref = db.reference('/')
            print("[FIREBASE] Initialized successfully")
            
            # Start background sync thread
            self.should_sync = True
            self._start_sync_thread()  
        except Exception as e:
            print(f"[FIREBASE] Initialization error: {str(e)}")
            self.db_ref = None
    
    def _start_sync_thread(self):
        """Start background thread for periodic sync"""
        if not self.db_ref:
            return

        def sync_thread():
            while self.should_sync:
                try:
                    # Sync all data directly from SQLite
                    self.sync_db_to_firebase()
                    print("[FIREBASE] Database sync completed")
                    
                    # Sleep for 5 minutes before next sync
                    time.sleep(300)
                except Exception as e:
                    print(f"[FIREBASE] Sync error: {str(e)}")
                    time.sleep(60)  # Shorter retry on error
        
        thread = threading.Thread(target=sync_thread, daemon=True)
        thread.start()
        print("[FIREBASE] Background sync thread started")
    
    def sync_db_to_firebase(self):
        """Sync entire database to Firebase directly from SQLite"""
        if not self.db_ref:
            return False
        
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            # Get all rows as dictionaries
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Data to sync
            firebase_data = {}
            
            # Get data from each table
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Convert rows to dictionaries
                firebase_data[table_name] = {}
                for row in rows:
                    row_dict = {key: row[key] for key in row.keys()}
                    
                    # Convert bool values (SQLite stores as 0/1)
                    if 'authorized' in row_dict:
                        row_dict['authorized'] = bool(row_dict['authorized'])
                    
                    # Use ID as key if it exists
                    if 'id' in row_dict:
                        firebase_data[table_name][str(row_dict['id'])] = row_dict
                    
            firebase_data['metadata'] = {
                'last_sync': datetime.now().isoformat(),
                'device_name': os.uname().nodename if hasattr(os, 'uname') else 'Unknown'
            }
            
            # Update Firebase
            self.db_ref.set(firebase_data)
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"[FIREBASE] Sync error: {str(e)}")
            return False
    
    def force_sync(self):
        """Manually trigger a sync"""
        return self.sync_db_to_firebase()
    
    def cleanup(self):
        """Stop background sync"""
        self.should_sync = False
        print("[FIREBASE] Sync thread stopped")
            

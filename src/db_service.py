import sqlite3
from datetime import datetime
import os
import uuid
import cv2 

class DatabaseService:
    def __init__(self):
        # Create directories if they don't exist
        os.makedirs('db', exist_ok=True)
        os.makedirs('db/intruder_images', exist_ok=True)
        self.db_path = 'db/security.db'
        self.images_path = 'db/intruder_images'
        self.init_db()

    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update access_logs table to include image path
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                name TEXT NOT NULL,
                authorized BOOLEAN NOT NULL,
                unlock_method TEXT NOT NULL,
                image_path TEXT
            )
        ''')

        # Create system_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def log_access(self, name, authorized, frame=None, unlock_method="face"):
        """Log access attempts with optional image storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        image_path = None
        if not authorized and frame is not None:
            # Generate unique filename for unauthorized access image
            image_filename = f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.jpg"
            image_path = os.path.join(self.images_path, image_filename)
            
            # Save the image
            cv2.imwrite(image_path, frame)
        
        cursor.execute('''
            INSERT INTO access_logs (timestamp, name, authorized, unlock_method, image_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now(), name, authorized, unlock_method, image_path))
        
        conn.commit()
        conn.close()

    def log_system_event(self, event_type, details):
        """Log system events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_logs (timestamp, event_type, details)
            VALUES (?, ?, ?)
        ''', (datetime.now(), event_type, details))
        
        conn.commit()
        conn.close()

    def get_recent_access_logs(self, limit=10):
        """Get recent access attempts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, name, authorized, unlock_method
            FROM access_logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        return logs

    def get_unauthorized_attempts(self, since=None):
        """Get unauthorized access attempts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if since:
            cursor.execute('''
                SELECT timestamp, name, unlock_method
                FROM access_logs
                WHERE authorized = 0 AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (since,))
        else:
            cursor.execute('''
                SELECT timestamp, name, unlock_method
                FROM access_logs
                WHERE authorized = 0
                ORDER BY timestamp DESC
            ''')
        
        logs = cursor.fetchall()
        conn.close()
        return logs
    

def print_recent_access_attempts():
    db = DatabaseService()
    logs = db.get_recent_access_logs(10)
    print("\nRecent Access Attempts:")
    print("-" * 80)
    for log in logs:
        timestamp, name, authorized, unlock_method = log
        status = "AUTHORIZED" if authorized else "UNAUTHORIZED"
        print(f"{timestamp} | {name:15} | {status:12} | {unlock_method}")

def print_unauthorized_attempts_today():
    db = DatabaseService()
    today = datetime.now().replace(hour=0, minute=0, second=0)
    logs = db.get_unauthorized_attempts(since=today)
    print("\nUnauthorized Attempts Today:")
    print("-" * 80)
    for log in logs:
        timestamp, name, unlock_method = log
        print(f"{timestamp} | {name:15} | {unlock_method}")

if __name__ == "__main__":
    print_recent_access_attempts()
    print_unauthorized_attempts_today()
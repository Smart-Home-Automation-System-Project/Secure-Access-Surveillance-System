import sqlite3
from datetime import datetime
import os
from cloud.cloudinary_service import CloudinaryService

class DatabaseService:
    def __init__(self):
        # Create directories if they don't exist
        os.makedirs('./db/intruder_images', exist_ok=True)
        self.db_path = './db/security.db'
        self.init_db()
        self.cloud_service = CloudinaryService()

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

        # Create user table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                authorized BOOLEAN NOT NULL
            )
        ''')

        # Create authorized_pins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_pins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pin TEXT NOT NULL UNIQUE
            )
        ''')


        conn.commit()
        conn.close()

    def log_access(self, name, authorized, frame=None, unlock_method="face"):
        """Log access attempts with optional image storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # If not authorized and frame is provided, upload the image
        image_path = None
        if not authorized and frame is not None:
            image_path = self.cloud_service.upload_image(frame)


        cursor.execute('''
            INSERT INTO access_logs (timestamp, name, authorized, unlock_method, image_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now(), name, authorized, unlock_method, image_path))
        
        conn.commit()
        conn.close()

    def add_user(self, name, authorized=True):
        """Add a new user to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (name, authorized)
                VALUES (?, ?)
            ''', (name, authorized))
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"[WARNING] User {name} already exists.")
        
        conn.close()

    def remove_user(self, name):
        """Remove a user from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM users
            WHERE name = ?
        ''', (name,))
        
        conn.commit()
        conn.close()

    def get_authorized_users(self):
        """Get all authorized users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name
            FROM users
            WHERE authorized = 1
        ''')
        
        users = cursor.fetchall()
        conn.close()
        # Convert tuple of tuples to list of names
        return [user[0] for user in users]
    
    def add_pin(self, pin):
        """Add a new authorized PIN to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO authorized_pins (pin)
                VALUES (?)
            ''', (pin,))
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"[WARNING] PIN {pin} already exists.")
        
        conn.close()

    def remove_pin(self, pin):
        """Remove a PIN from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM authorized_pins
            WHERE pin = ?
        ''', (pin,))
        
        conn.commit()
        conn.close()

    def get_pins(self):
        """Get PIN details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pin
            FROM authorized_pins
        ''')
        
        pin_details = cursor.fetchone()
        conn.close()
        return pin_details

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
    
    def get_unauthorized_attempts_with_images(self, limit=10):
        """Get unauthorized access attempts with Cloudinary URLs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, name, image_path
            FROM access_logs
            WHERE authorized = 0 AND image_path IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        return logs
    
    def get_all_tables_and_data(self):
        """Get all tables and their data from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute('''
            SELECT name FROM sqlite_master WHERE type='table'
        ''')
        tables = cursor.fetchall()
        
        all_data = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f'SELECT * FROM {table_name}')
            all_data[table_name] = cursor.fetchall()
        
        conn.close()
        return all_data
    
    def get_all_users(self):
        """Get all users from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT name
                FROM users
                ORDER BY name
            """)
            users = cursor.fetchall()
            # Convert tuple of tuples to list of names
            return [user[0] for user in users]
        except Exception as e:
            print(f"Error retrieving users: {e}")
            return []
        finally:
            conn.close()

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

def print_all_tables_and_data():
    db = DatabaseService()
    all_data = db.get_all_tables_and_data()
    for table_name, data in all_data.items():
        print(f"\nTable: {table_name}")
        print("-" * 80)
        for row in data:
            print(row)


def get_authorized_users():
    db = DatabaseService()
    return db.get_authorized_users()
    
def get_pins():
    db = DatabaseService()
    return db.get_pins()
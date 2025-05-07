import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys
import sqlite3
from datetime import datetime
import numpy as np

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.db_service import DatabaseService


class TestDatabaseService(unittest.TestCase):
    
    @patch('os.makedirs')
    @patch('sqlite3.connect')
    @patch('db.db_service.CloudinaryService')
    def setUp(self, mock_cloudinary_class, mock_connect, mock_makedirs):
        """Set up test environment"""
        # Create mock for sqlite connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        mock_connect.return_value = self.mock_conn
        
        # Create mock for cloudinary service
        self.mock_cloudinary = MagicMock()
        mock_cloudinary_class.return_value = self.mock_cloudinary
        
        # Create database service instance
        self.db = DatabaseService()
        
        # Store mocks for later use
        self.mock_connect = mock_connect
    
    def test_initialization(self):
        """Test database initialization"""
        # Check path was set correctly
        self.assertEqual(self.db.db_path, './db/security.db')
        
        # Check tables were created
        calls = self.mock_cursor.execute.call_args_list
        table_creation_calls = [call for call in calls if 'CREATE TABLE IF NOT EXISTS' in call[0][0]]
        self.assertGreaterEqual(len(table_creation_calls), 3)  # At least 3 tables created
        
        # Check commit was called
        self.mock_conn.commit.assert_called()
    
    @patch('sqlite3.connect')
    def test_log_access_authorized(self, mock_connect):
        """Test logging authorized access"""
        # Set up mock connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Log an authorized access
        self.db.log_access("TestUser", True, unlock_method="face")
        
        # Check SQL was executed correctly
        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        self.assertIn("INSERT INTO access_logs", args[0])
        self.assertEqual(args[1][1], "TestUser")
        self.assertEqual(args[1][2], True)
        self.assertEqual(args[1][3], "face")
        
        # Check commit was called
        mock_conn.commit.assert_called_once()
        
        # Cloudinary should not be called for authorized access
        self.mock_cloudinary.upload_image.assert_not_called()
    
    @patch('sqlite3.connect')
    def test_log_access_unauthorized_with_image(self, mock_connect):
        """Test logging unauthorized access with image"""
        # Set up mock connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Set up mock for cloudinary
        self.mock_cloudinary.upload_image.return_value = "https://example.com/image.jpg"
        
        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Log an unauthorized access with image
        self.db.log_access("Unknown", False, frame=test_frame, unlock_method="face")
        
        # Check cloudinary was called
        self.mock_cloudinary.upload_image.assert_called_once_with(test_frame)
        
        # Check SQL was executed correctly
        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        self.assertIn("INSERT INTO access_logs", args[0])
        self.assertEqual(args[1][1], "Unknown")
        self.assertEqual(args[1][2], False)
        self.assertEqual(args[1][3], "face")
        self.assertEqual(args[1][4], "https://example.com/image.jpg")
        
        # Check commit was called
        mock_conn.commit.assert_called_once()
    
    @patch('sqlite3.connect')
    def test_add_user(self, mock_connect):
        """Test adding a user"""
        # Set up mock connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Add a user
        self.db.add_user("NewUser", True)
        
        # Check SQL was executed correctly
        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        self.assertIn("INSERT INTO users", args[0])
        self.assertEqual(args[1][0], "NewUser")
        self.assertEqual(args[1][1], True)
        
        # Check commit was called
        mock_conn.commit.assert_called_once()
    
    @patch('sqlite3.connect')
    def test_add_user_duplicate(self, mock_connect):
        """Test adding a duplicate user"""
        # Set up mock connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Set up cursor to raise IntegrityError
        mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")
        
        # Add a duplicate user
        self.db.add_user("ExistingUser", True)
        
        # Check SQL was executed
        mock_cursor.execute.assert_called_once()
        
        # Commit should not be called due to IntegrityError
        mock_conn.commit.assert_not_called()
    
    @patch('sqlite3.connect')
    def test_add_pin(self, mock_connect):
        """Test adding a PIN"""
        # Set up mock connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Add a PIN
        self.db.add_pin("1234")
        
        # Check SQL was executed correctly
        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        self.assertIn("INSERT INTO authorized_pins", args[0])
        self.assertEqual(args[1][0], "1234")
        
        # Check commit was called
        mock_conn.commit.assert_called_once()

    @patch('sqlite3.connect')
    def test_get_authorized_users(self, mock_connect):
        """Test getting authorized users"""
        # Set up mock connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Set up cursor to return a mock result
        mock_cursor.fetchone.return_value = ("AuthorizedUser",)
        
        # Get authorized users
        result = self.db.get_authorized_users()
        
        # Check SQL was executed correctly
        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        # Use a simplified assertion that ignores whitespace
        self.assertIn("SELECT name", args[0])
        self.assertIn("FROM users", args[0])
        self.assertIn("WHERE authorized = 1", args[0])

    @patch('sqlite3.connect')
    def test_get_pins(self, mock_connect):
        """Test getting PIN details"""
        # Set up mock connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Set up cursor to return a mock result
        mock_cursor.fetchone.return_value = ("1234",)
        
        # Get PINs
        result = self.db.get_pins()
        
        # Check SQL was executed correctly
        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        # Use a simplified assertion that ignores whitespace
        self.assertIn("SELECT pin", args[0])
        self.assertIn("FROM authorized_pins", args[0])

if __name__ == '__main__':
    unittest.main()
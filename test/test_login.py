# test/test_login.py

import unittest
from gui.login import login_user  # Adjust based on actual function in login.py

class TestLogin(unittest.TestCase):

    def test_valid_login(self):
        result = login_user("admin", "correct_password")
        self.assertTrue(result)

    def test_invalid_login(self):
        result = login_user("admin", "wrong_password")
        self.assertFalse(result)

    def test_empty_username(self):
        result = login_user("", "some_password")
        self.assertFalse(result)

    def test_empty_password(self):
        result = login_user("admin", "")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()

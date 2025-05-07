import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory so `gui` can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your target module
import gui.homepage as homepage

class TestHomepage(unittest.TestCase):

    @patch("gui.homepage.subprocess.Popen")  # ✅ Full path
    def test_start_now_runs_script(self, mock_popen):
        homepage.StartNow()
        self.assertTrue(mock_popen.called, "subprocess.Popen should be called in StartNow")

    @patch("gui.homepage.subprocess.Popen")  # ✅ Full path
    @patch("gui.homepage.open_popup")        # ✅ Full path
    def test_confirm_runs_script_and_popup(self, mock_popup, mock_popen):
        homepage.Confirm()
        self.assertTrue(mock_popen.called, "subprocess.Popen should be called in Confirm")
        self.assertTrue(mock_popup.called, "Popup should be called in Confirm")

if __name__ == "__main__":
    unittest.main()

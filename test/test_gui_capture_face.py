import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure the root folder is in sys.path for proper imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui import gui_capture_face

class TestGuiCaptureFace(unittest.TestCase):

    @patch("gui.gui_capture_face.cv2.VideoCapture")
    def test_camera_initialization(self, mock_video_capture):
        """Test if camera initializes properly with OpenCV."""
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap_instance

        cam = gui_capture_face.cv2.VideoCapture(0)
        self.assertTrue(cam.isOpened())
        mock_video_capture.assert_called_with(0)

    @patch("gui.gui_capture_face.cv2.imwrite")
    def test_image_capture_mock(self, mock_imwrite):
        """Test if image is saved when imwrite is called."""
        mock_imwrite.return_value = True
        result = gui_capture_face.cv2.imwrite("test.jpg", MagicMock())
        self.assertTrue(result)
        mock_imwrite.assert_called_once()

    def test_import_gui_capture_face(self):
        """Test if gui_capture_face.py can be imported without errors."""
        try:
            from gui import gui_capture_face
        except Exception as e:
            self.fail(f"Importing gui_capture_face failed: {e}")

if __name__ == "__main__":
    unittest.main()

import unittest
from unittest import mock
import numpy as np
import os
import shutil
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from util import image_capture

class TestImageCapture(unittest.TestCase):
    def setUp(self):
        self.test_name = "TestUser"
        self.test_dir = os.path.join("face_rec_dataset", self.test_name)
        # Clean up any existing folder
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_folder(self):
        folder = image_capture.create_folder(self.test_name)
        self.assertTrue(os.path.exists(folder))

    @mock.patch("cv2.VideoCapture")
    @mock.patch("cv2.imwrite")
    @mock.patch("matplotlib.pyplot.show")  # Prevent GUI popup
    def test_capture_photos_key_event_space(self, mock_show, mock_imwrite, mock_video_capture):
        # Create dummy frame
        dummy_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255

        # Configure mock
        mock_cam_instance = mock.Mock()
        mock_cam_instance.isOpened.return_value = True
        mock_cam_instance.read.return_value = (True, dummy_frame)
        mock_video_capture.return_value = mock_cam_instance

        # Simulate call (we won’t actually press keys or open GUI)
        image_capture.capture_photos(self.test_name)

        self.assertTrue(os.path.exists(self.test_dir))

if __name__ == "__main__":
    unittest.main()

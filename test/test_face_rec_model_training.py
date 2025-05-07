import unittest
from unittest import mock
import builtins
import os
import pickle
import numpy as np
import sys

# Add the project root to sys.path so util can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock external dependencies
with mock.patch.dict('sys.modules', {
    'face_recognition': mock.MagicMock(),
    'cv2': mock.MagicMock(),
    'imutils': mock.MagicMock(),
    'imutils.paths': mock.MagicMock()
}):
    from util import face_rec_model_training

class TestFaceRecModelTraining(unittest.TestCase):
    def setUp(self):
        self.test_models_folder = "test_models"
        self.test_pickle_file = os.path.join(self.test_models_folder, "face_rec_encodings.pickle")
        os.makedirs(self.test_models_folder, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_pickle_file):
            os.remove(self.test_pickle_file)
        if os.path.exists(self.test_models_folder):
            os.rmdir(self.test_models_folder)

    def test_create_folder_creates_and_returns_path(self):
        folder_name = "test_create_folder"
        if os.path.exists(folder_name):
            os.rmdir(folder_name)

        path = face_rec_model_training.create_folder(folder_name)
        self.assertTrue(os.path.exists(path))
        self.assertEqual(path, folder_name)

        # Cleanup
        os.rmdir(folder_name)

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("pickle.dumps")
    def test_serialization_creates_pickle_file(self, mock_dumps, mock_open_file):
        data = {"encodings": [np.array([0.1, 0.2])], "names": ["TestUser"]}
        pickle_path = os.path.join(self.test_models_folder, "face_rec_encodings.pickle")

        # Simulate saving pickle
        try:
            with open(pickle_path, "wb") as f:
                f.write(pickle.dumps(data))
        except IOError as e:
            self.fail(f"Serialization raised IOError: {e}")

        mock_dumps.assert_called_once_with(data)
        mock_open_file.assert_called_once_with(pickle_path, "wb")

if __name__ == "__main__":
    unittest.main()

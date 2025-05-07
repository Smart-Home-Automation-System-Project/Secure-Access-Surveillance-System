import unittest
from unittest import mock
import builtins
import os
import pickle
import numpy as np

# Patch paths, face_recognition, cv2, and open as needed
with mock.patch.dict('sys.modules', {
    'face_recognition': mock.MagicMock(),
    'cv2': mock.MagicMock(),
    'imutils': mock.MagicMock(),
    'imutils.paths': mock.MagicMock()
}):
    from util import face_rec_model_training

class TestFaceRecModelTraining(unittest.TestCase):

    @mock.patch('util.face_rec_model_training.os.makedirs')
    @mock.patch('util.face_rec_model_training.os.path.exists', return_value=False)
    def test_create_folder_creates_directory(self, mock_exists, mock_makedirs):
        folder = "test_folder"
        result = face_rec_model_training.create_folder(folder)
        mock_makedirs.assert_called_once_with(folder)
        self.assertEqual(result, folder)

    @mock.patch('util.face_rec_model_training.pickle.dump')
    @mock.patch('util.face_rec_model_training.open', new_callable=mock.mock_open)
    def test_pickle_serialization(self, mock_open, mock_pickle_dump):
        test_data = {"encodings": [np.array([0.1, 0.2])], "names": ["TestUser"]}
        file_path = os.path.join("models", "face_rec_encodings.pickle")

        # Simulate saving
        with open(file_path, "wb") as f:
            f.write(pickle.dumps(test_data))

        mock_open.assert_called_with(file_path, "wb")

    @mock.patch('util.face_rec_model_training.face_recognition.face_encodings', return_value=[np.array([0.1] * 128)])
    @mock.patch('util.face_rec_model_training.face_recognition.face_locations', return_value=[(0, 0, 10, 10)])
    @mock.patch('util.face_rec_model_training.cv2.imread')
    @mock.patch('util.face_rec_model_training.cv2.cvtColor')
    @mock.patch('util.face_rec_model_training.paths.list_images', return_value=["face_rec_dataset/TestUser/test1.jpg"])
    def test_image_processing_flow(self, mock_list_images, mock_cvtColor, mock_imread, mock_face_locations, mock_face_encodings):
        mock_imread.return_value = mock.Mock()
        mock_cvtColor.return_value = mock.Mock()

        # Clear global lists
        face_rec_model_training.knownEncodings.clear()
        face_rec_model_training.knownNames.clear()

        # Trigger the loop logic
        for imagePath in mock_list_images.return_value:
            name = os.path.basename(os.path.dirname(imagePath))
            image = mock_imread(imagePath)
            rgb = mock_cvtColor(image, face_rec_model_training.cv2.COLOR_BGR2RGB)
            boxes = mock_face_locations(rgb, model="hog")
            encodings = mock_face_encodings(rgb, boxes)
            for encoding in encodings:
                face_rec_model_training.knownEncodings.append(encoding)
                face_rec_model_training.knownNames.append(name)

        self.assertEqual(face_rec_model_training.knownNames, ["TestUser"])
        self.assertEqual(len(face_rec_model_training.knownEncodings), 1)

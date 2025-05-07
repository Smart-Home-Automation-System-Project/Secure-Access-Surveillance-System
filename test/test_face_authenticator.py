import pytest
import builtins
import pickle
from unittest.mock import patch, MagicMock
from auth.face_authenticator import FaceAuthenticator

# Helper function to mock pickle file content
def fake_pickle_data():
    return pickle.dumps({
        "encodings": [[0.1, 0.2, 0.3]],  # Fake face encoding data
        "names": ["TestUser"]
    })

@patch("builtins.open")
@patch("auth.face_authenticator.get_authorized_users")

@patch("camera.camera_manager.CameraManager.get_instance")
def test_face_authenticator_init(mock_camera_instance, mock_get_users, mock_open):
    # Mock pickle file content
    fake_file = MagicMock()
    fake_file.read.return_value = fake_pickle_data()
    mock_open.return_value.__enter__.return_value = fake_file

    # Mock authorized users
    mock_get_users.return_value = ["TestUser"]

    # Mock camera instance
    mock_camera = MagicMock()
    mock_camera.get_frame.return_value = None  # We don't want real frames
    mock_camera_instance.return_value = mock_camera

    # Now, create the FaceAuthenticator instance
    auth = FaceAuthenticator()

    # Check that known names are loaded
    assert auth.known_face_names == ["TestUser"]

    # Check that authorized names are loaded
    assert auth.authorized_names == ["TestUser"]

    # Check that the camera is acquired
    mock_camera.acquire.assert_called_once()


import sys
sys.path.append(r"E:\sem 04\Secure-Access-Surveillance-System")

import pytest
from unittest.mock import patch, MagicMock
from flask import Response

# ✅ Corrected import (your video_stream.py is inside camera/)
from camera.video_stream import app, init_camera, get_camera_feed, video_feed, stop_stream, start_stream

# ---------------------- TEST CASES ------------------------

@patch("camera.camera_manager.CameraManager.get_instance")
def test_init_camera(mock_camera_instance):
    mock_camera = MagicMock()
    mock_camera.is_frame_available.return_value = True
    mock_camera_instance.return_value = mock_camera

    result = init_camera()
    assert result is True

@patch("camera.camera_manager.CameraManager.get_instance")
def test_get_camera_feed(mock_camera_instance):
    mock_camera = MagicMock()
    mock_camera.get_frame.return_value = MagicMock()
    mock_camera_instance.return_value = mock_camera

    generator = get_camera_feed()
    frame = next(generator)
    assert b'--frame' in frame

def test_video_feed_route():
    response = video_feed()
    assert isinstance(response, Response)

@patch("camera.camera_manager.CameraManager.get_instance")
def test_stop_stream(mock_camera_instance):
    mock_camera = MagicMock()
    mock_camera.release = MagicMock()
    mock_camera_instance.return_value = mock_camera

    stop_stream()
    mock_camera.release.assert_called()

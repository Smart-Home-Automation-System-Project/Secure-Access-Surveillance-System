import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import numpy as np
import threading
import time
from unittest.mock import patch, MagicMock, Mock
from flask import Response

# Import the modules being tested
from camera.video_stream import app, init_camera, get_camera_feed, video_feed, stop_stream, start_stream, start_stream_thread

# ---------------------- TEST CASES ------------------------

@patch("camera.camera_manager.CameraManager.get_instance")
def test_init_camera(mock_camera_instance):
    mock_camera = MagicMock()
    mock_camera.is_frame_available.return_value = True
    mock_camera_instance.return_value = mock_camera

    result = init_camera()
    assert result is True
    mock_camera.acquire.assert_called_once()

# @patch("camera.video_stream.stream_active", True)  # Match the actual variable name
# @patch("camera.video_stream.camera_manager")
# def test_get_camera_feed(mock_camera_manager):
#     # Create a test frame
#     test_frame = np.zeros((120, 160, 3), dtype=np.uint8)
#     mock_camera_manager.get_frame.return_value = test_frame
    
#     # Mock cv2.imencode to return a valid jpeg
#     with patch('cv2.imencode') as mock_imencode:
#         mock_imencode.return_value = (True, b'fake-jpeg-data')
        
#         # Get the generator
#         generator = get_camera_feed()
        
#         # Set stream_active to False after getting the first frame to avoid infinite loop
#         with patch("camera.video_stream.stream_active", False):
#             # Get the first frame
#             frame = next(generator)
            
#             # Assert correct formatting
#             assert b'--frame' in frame
#             assert b'Content-Type: image/jpeg' in frame
#             assert b'fake-jpeg-data' in frame
        
#     # Verify the mocks were called correctly
#     mock_camera_manager.get_frame.assert_called_once()
#     mock_imencode.assert_called_once()

# @patch("camera.video_stream.get_camera_feed")
# def test_video_feed_route(mock_get_camera_feed):
#     # Mock the generator to return a simple value
#     mock_get_camera_feed.return_value = (f"frame{i}".encode() for i in range(1))
    
#     # Test the route
#     response = video_feed()
#     assert isinstance(response, Response)
#     assert response.mimetype == 'multipart/x-mixed-replace; boundary=frame'

# @patch("camera.video_stream.camera_manager")
# def test_stop_stream(mock_camera_manager):
#     # Test the stop_stream function
#     with patch("camera.video_stream.stream_active", True):
#         stop_stream()
        
#         # Verify stream_active is set to False
#         from camera.video_stream import stream_active
#         assert not stream_active
        
#         # Verify camera is released
#         mock_camera_manager.release.assert_called_once()

@patch("threading.Thread")
@patch("camera.video_stream.init_camera")
def test_start_stream_thread(mock_init_camera, mock_thread):
    # Mock initialization
    mock_init_camera.return_value = True
    mock_thread_instance = MagicMock()
    mock_thread.return_value = mock_thread_instance
    
    # Call the function
    result = start_stream_thread()
    
    # Verify thread was created and started
    mock_thread.assert_called_once()
    mock_thread_instance.start.assert_called_once()
    assert result == mock_thread_instance

@patch("camera.video_stream.app.run")
@patch("camera.video_stream.init_camera")
def test_start_stream(mock_init_camera, mock_app_run):
    # Mock initialization
    mock_init_camera.return_value = True
    
    # Mock os.getenv to return our test values
    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key, default: {
            'STREAM_PORT': '5001',
            'STREAM_HOST': '127.0.0.1'
        }.get(key, default)
        
        # Call the function
        start_stream()
        
        # Verify stream_active is True
        from camera.video_stream import stream_active
        assert stream_active is True
        
        # Verify app.run was called with correct parameters
        mock_app_run.assert_called_once_with(host='127.0.0.1', port=5001, threaded=True)

@patch("camera.video_stream.init_camera")
def test_start_stream_with_camera_error(mock_init_camera):
    # Mock initialization failure
    mock_init_camera.return_value = False
    
    # Call the function - should print error but not crash
    with patch('builtins.print') as mock_print:
        start_stream()
        mock_print.assert_called_with("[ERROR] Could not initialize camera")

if __name__ == "__main__":
    pytest.main(["-v"])
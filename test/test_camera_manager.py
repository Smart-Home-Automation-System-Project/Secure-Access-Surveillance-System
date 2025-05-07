import pytest
from unittest.mock import patch, MagicMock
from camera.camera_manager import CameraManager

@patch("camera.camera_manager.cv2.VideoCapture")
def test_get_instance_returns_singleton(mock_video_capture):
    mock_cam = MagicMock()
    mock_video_capture.return_value = mock_cam
    mock_cam.isOpened.return_value = True
    mock_cam.read.return_value = (True, MagicMock())  # ✅ Fix for thread error

    cam1 = CameraManager.get_instance(0)
    cam2 = CameraManager.get_instance(0)

    assert cam1 is cam2  # Singleton

@patch("camera.camera_manager.cv2.VideoCapture")
def test_acquire_and_release(mock_video_capture):
    mock_cam = MagicMock()
    mock_video_capture.return_value = mock_cam
    mock_cam.isOpened.return_value = True
    mock_cam.read.return_value = (True, MagicMock())  # ✅ Fix for thread error

    cam = CameraManager.get_instance(0)

    ref1 = cam.acquire()
    ref2 = cam.acquire()

    assert ref1 == 1
    assert ref2 == 2

    ref3 = cam.release()
    assert ref3 == 1

    ref4 = cam.release()
    assert ref4 == 0

@patch("camera.camera_manager.cv2.VideoCapture")
def test_get_frame(mock_video_capture):
    mock_cam = MagicMock()
    mock_video_capture.return_value = mock_cam
    mock_cam.isOpened.return_value = True
    mock_cam.read.return_value = (True, MagicMock())  # ✅ Fix for thread error

    cam = CameraManager.get_instance(1)  # Different index to avoid interference

    fake_frame = MagicMock()
    with cam.lock:
        cam.frame = fake_frame

    result_frame = cam.get_frame()
    assert result_frame is not None

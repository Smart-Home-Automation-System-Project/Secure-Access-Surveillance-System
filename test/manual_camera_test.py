import time
from camera.camera_manager import CameraManager

def test_camera_manager_without_mocking():
    # Get real camera instance (camera index 0)
    cam = CameraManager.get_instance(0)

    # Register usage
    cam.acquire()

    # Wait for a couple of frames to be captured by the background thread
    print("[TEST] Waiting 3 seconds for camera to grab some frames...")
    time.sleep(3)

    # Try to get a frame
    frame = cam.get_frame()

    assert frame is not None, "No frame was captured from the camera!"

    print("[TEST] Frame successfully captured.")

    # Release the camera
    cam.release()

if __name__ == "__main__":
    test_camera_manager_without_mocking()

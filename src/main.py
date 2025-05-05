from door_lock_handler import DoorLockHandler
import threading
from video_stream import start_stream, stop_stream

if __name__ == "__main__":
    door = DoorLockHandler()
    
    # Start video stream in a separate thread
    video_thread = threading.Thread(target=start_stream)
    video_thread.daemon = True  # Thread will be terminated when main program exits
    video_thread.start()
    
    try:
        door.start()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        door.stop()
        stop_stream()  # Stop the video stream
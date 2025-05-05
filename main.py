from handlers.door_lock_handler import DoorLockHandler
from camera.video_stream import start_stream_thread, stop_stream
from db.firebase_service import FirebaseService

if __name__ == "__main__":
    door = DoorLockHandler()
    firebase = FirebaseService()
    start_stream_thread()
    
    try:
        door.start()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        door.stop()
        firebase.cleanup()
        stop_stream()
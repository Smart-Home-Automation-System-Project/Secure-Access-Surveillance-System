from handlers.door_lock_handler import DoorLockHandler
from camera.video_stream import start_stream_thread, stop_stream
from db.firebase_service import FirebaseService
from gui.login import Login

if __name__ == "__main__":
    # door_lock_handler = DoorLockHandler()
    # firebase = FirebaseService()
    # start_stream_thread()

    # try:
    #     door_lock_handler.start()
    # except Exception as e:
    #     print(f"Error: {e}")
    # finally:
    #     door_lock_handler.stop()
    #     firebase.cleanup()
    #     stop_stream()

    Login()
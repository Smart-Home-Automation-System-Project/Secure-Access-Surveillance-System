from door_lock_handler import DoorLockHandler

if __name__ == "__main__":
    door = DoorLockHandler()
    try:
        door.start()
    except Exception as e:
        print(f"Error: {e}")
        door.stop()
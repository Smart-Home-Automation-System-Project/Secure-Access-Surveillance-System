from datetime import datetime, timedelta
import threading
import time
from face_authenticator import FaceAuthenticator
from mqtt_service import MQTTService
from db_service import DatabaseService
import json

class DoorLockHandler:
    def __init__(self):
        self.is_locked = True
        self.unlock_time = None
        self.unlock_duration = 300  # 5 minutes for face auth 
        self.auth = FaceAuthenticator()
        self.auth_thread = None
        self.running = False
        self.last_locked_time = None
        self.cooldown_duration = 10
        self.unlocked_by_pin = False
        self.mqtt = MQTTService()
        self.db = DatabaseService()

        # Load authorized pins from JSON file
        try:
            with open("config/auth_config.json", "r") as f:
                config = json.load(f)
                self.valid_pins = config["authorized_pins"]
                print(f"[INFO] Loaded {len(self.valid_pins)} authorized pins")
        except FileNotFoundError:
            print("[WARNING] auth_config.json not found!")

    def unlock(self, by_pin=False):
        """Unlock the door"""
        self.is_locked = False
        self.unlocked_by_pin = by_pin
        if not by_pin:
            self.unlock_time = datetime.now()
            print("[DOOR] Unlocked for 5 minutes")
        else:
            self.unlock_time = None
            print("[DOOR] Unlocked indefinitely by PIN")

    def lock(self):
        """Lock the door"""
        self.is_locked = True
        self.unlock_time = None
        self.unlocked_by_pin = False
        self.last_locked_time = datetime.now()
        print("[DOOR] Locked")

    def check_status(self):
        """Check if door should auto-lock"""
        if not self.is_locked and not self.unlocked_by_pin and self.unlock_time:
            if datetime.now() - self.unlock_time > timedelta(seconds=self.unlock_duration):
                self.lock()
        return self.is_locked

    def unlock_with_pin(self, pin):
        """Try to unlock door with PIN"""
        if pin in self.valid_pins:
            self.unlock(by_pin=True)
            # Log the access attempt
            self.db.log_access("UNKNOWN", True, unlock_method="PIN")
            return True
        return False

    def _face_auth_loop(self):
        """Background face authentication loop"""
        last_detection_time = 0
        last_alert_time = 0
        while self.running:
            name, authorized = self.auth.check_authentication()
            current_time = time.time()
            
            if name != "No face detected" and (current_time - last_detection_time) >= 1:
                # Check cooldown period before unlocking
                if authorized and self.is_locked:
                    if self.last_locked_time is None or \
                       (datetime.now() - self.last_locked_time).total_seconds() > self.cooldown_duration:
                        print(f"[FACE] Authorized user: {name}")
                        # Log the access attempt
                        self.db.log_access(name, authorized)
                        self.unlock(by_pin=False)
                elif not authorized and self.is_locked:
                    # Wait 5 minutes before sending another alert
                    if name != "Unauthorized" and (current_time - last_alert_time) >= 300:  # 5 minutes cooldown
                        print(f"[FACE] Unauthorized access detected: {name}")
                        ret, frame = self.auth.cap.read()
                        if ret:
                            self.db.log_access(name, authorized, frame=frame)
                        else:
                            print("[FACE] Failed to capture frame for alert")
                            self.db.log_access(name, authorized)
                        last_alert_time = current_time
                last_detection_time = current_time
            
            self.check_status()
            time.sleep(0.1)

    def start(self):
        """Start the door control system"""
        self.running = True
        self.auth_thread = threading.Thread(target=self._face_auth_loop)
        self.auth_thread.start()
        print("Door Control System Ready")
        print("Commands: lock, status, pin XXXX, exit")
        print("Note: PIN unlock has no time limit. Use 'lock' to manually lock")

        while self.running:
            try:
                command = input().strip().lower()
                if command == "exit":
                    self.stop()
                elif command == "status":
                    status = "locked" if self.is_locked else "unlocked"
                    unlock_method = " (by PIN)" if self.unlocked_by_pin else ""
                    print(f"[DOOR] Status: {status}{unlock_method}")
                elif command == "lock":
                    self.lock()
                elif command.startswith("pin "):
                    pin = command.split()[1]
                    if not self.unlock_with_pin(pin):
                        print("[DOOR] Invalid PIN")
                else:
                    print("Invalid command")
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        """Stop the door control system"""
        self.running = False
        if self.auth_thread:
            self.auth_thread.join()
        self.auth.cleanup()
        print("\nDoor control system stopped")

if __name__ == "__main__":
    door = DoorLockHandler()
    try:
        door.start()
    except Exception as e:
        print(f"Error: {e}")
        door.stop()
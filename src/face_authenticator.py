import face_recognition
import cv2
import numpy as np
import pickle
import time
from db.db_service import get_authorized_users

class FaceAuthenticator:
    def __init__(self):
        # Load pre-trained face encodings
        print("[INFO] loading encodings...")
        with open("models/face_rec_encodings.pickle", "rb") as f:
            data = pickle.loads(f.read())
        self.known_face_encodings = data["encodings"]
        self.known_face_names = data["names"]
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Lower resolution for faster processing
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Configuration
        self.cv_scaler = 4
        
        # Load authorized users from database
        self.authorized_names = []
        try:
            users = get_authorized_users()
            if users is not None:
                self.authorized_names = users
                print(f"[INFO] Loaded {len(self.authorized_names)} authorized users")
            else:
                print("[WARNING] No authorized users found in database")
        except FileNotFoundError:
            print("[WARNING] Failed to load authorized users from database")
        except Exception as e:
            print(f"[ERROR] Failed to load authorized users: {e}")

    def check_authentication(self):
        """Capture frame and return authentication status"""
        ret, frame = self.cap.read()
        if not ret:
            return "No frame", False
        
        # Resize frame for faster processing
        resized_frame = cv2.resize(frame, (0, 0), fx=(1/self.cv_scaler), fy=(1/self.cv_scaler))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        # First check if any face is detected
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            return "No face detected", False
        
        # Only proceed with recognition if faces are detected
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, model='large')
        detected_name = "Unknown"
        is_authorized = False
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            
            if True in matches:
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    detected_name = name
                    if name in self.authorized_names:
                        is_authorized = True
                    break  # Exit after first match
        
        return detected_name, is_authorized

    # debugging function to check authentication
    def run(self):
        """Run continuous authentication"""
        last_detection_time = 0
        try:
            while True:
                name, authorized = self.check_authentication()
                
                # Only print when a face is detected and not too frequently
                current_time = time.time()
                if name != "No face detected" and (current_time - last_detection_time) >= 1:
                    status = "AUTHORIZED" if authorized else "UNAUTHORIZED"
                    print(f"User: {name} - Status: {status}")
                    last_detection_time = current_time
                
                time.sleep(0.1)  # Small delay to prevent CPU overload
                
        except KeyboardInterrupt:
            print("\nStopping authentication system...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Release resources"""
        self.cap.release()

if __name__ == "__main__":
    auth_system = FaceAuthenticator()
    auth_system.run()
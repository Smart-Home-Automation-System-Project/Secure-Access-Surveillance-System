import face_recognition
import cv2
import numpy as np
import time
import pickle
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load pre-trained face encodings
print("[INFO] loading encodings...")
with open("models/encodings.pickle", "rb") as f:  # Updated path to the pickle file
    data = pickle.loads(f.read())
known_face_encodings = data["encodings"]
known_face_names = data["names"]

# Initialize the webcam
cap = cv2.VideoCapture(0)  # 0 is usually the default webcam index

# Optional: Set resolution if needed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Variables
cv_scaler = 4
face_locations = []
face_encodings = []
face_names = []
frame_count = 0
start_time = time.time()
fps = 0

authorized_names = ["suraja"]

# Set up matplotlib figure and axis
fig, ax = plt.subplots()
ax.axis("off")  # Turn off axes

# Set up a placeholder for the image
img_placeholder = ax.imshow(np.zeros((1080, 1920, 3), dtype=np.uint8))

def process_frame(frame):
    global face_locations, face_encodings, face_names

    resized_frame = cv2.resize(frame, (0, 0), fx=(1/cv_scaler), fy=(1/cv_scaler))
    rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_resized_frame)
    face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations, model='large')

    face_names = []
    authorized_face_detected = False

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            if name in authorized_names:
                authorized_face_detected = True
        face_names.append(name)

    # Print lock or unlock status based on authorization
    if authorized_face_detected:
        print("Unlock")
    else:
        print("Lock")

    return frame

def draw_results(frame):
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= cv_scaler
        right *= cv_scaler
        bottom *= cv_scaler
        left *= cv_scaler

        cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 3)
        cv2.rectangle(frame, (left - 3, top - 35), (right + 3, top), (244, 42, 3), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)

        if name in authorized_names:
            cv2.putText(frame, "Authorized", (left + 6, bottom + 23), font, 0.6, (0, 255, 0), 1)
    return frame

def calculate_fps():
    global frame_count, start_time, fps
    frame_count += 1
    elapsed_time = time.time() - start_time
    if elapsed_time > 1:
        fps = frame_count / elapsed_time
        frame_count = 0
        start_time = time.time()
    return fps

# Define a function for updating the image in matplotlib
def update_frame(frame):
    processed_frame = process_frame(frame)
    display_frame = draw_results(processed_frame)
    current_fps = calculate_fps()

    cv2.putText(display_frame, f"FPS: {current_fps:.1f}", (display_frame.shape[1] - 150, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    img_placeholder.set_data(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB))

# Create an animation function
def animate(i):
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        return

    update_frame(frame)

# Create animation
ani = FuncAnimation(fig, animate, interval=50)

plt.show()

cap.release()

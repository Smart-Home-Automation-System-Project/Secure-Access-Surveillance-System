import os
from imutils import paths
import face_recognition
import pickle
import cv2

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

print("[INFO] Starting face processing...")

# Define dataset and models folder
dataset_folder = "face_rec_dataset"
models_folder = create_folder("models")

# Initialize lists for encodings and names
knownEncodings = []
knownNames = []

# Get image paths from the dataset folder
imagePaths = list(paths.list_images(dataset_folder))

for (i, imagePath) in enumerate(imagePaths):
    print(f"[INFO] Processing image {i + 1}/{len(imagePaths)}")
    name = os.path.basename(os.path.dirname(imagePath))  # Extract the person's name from the folder structure
    
    # Load the image and convert it to RGB
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Detect face locations and compute encodings
    boxes = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, boxes)
    
    # Append encodings and names to the respective lists
    for encoding in encodings:
        knownEncodings.append(encoding)
        knownNames.append(name)

print("[INFO] Serializing encodings...")

# Save the encodings and names to a pickle file
data = {"encodings": knownEncodings, "names": knownNames}
pickle_file_path = os.path.join(models_folder, "face_rec_encodings.pickle")

try:
    with open(pickle_file_path, "wb") as f:
        f.write(pickle.dumps(data))
    print(f"[INFO] Training complete. Encodings saved to '{pickle_file_path}'")
except IOError as e:
    print(f"[ERROR] Failed to save encodings: {e}")
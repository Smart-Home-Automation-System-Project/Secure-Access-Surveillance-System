import cv2
import os
from datetime import datetime
import time
import shutil
import easyocr
import re
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

# Configure paths
PLATE_FOLDER = "plate/"
VEHICLE_FOLDER = "plate1/"
SUSPECT_FOLDER = "plate1/suspect/"
MOST_CLEARED_FOLDER = "most_cleared/"
CAPTURE_INTERVAL = 5  # seconds

# Create folders if they don't exist
os.makedirs(PLATE_FOLDER, exist_ok=True)
os.makedirs(VEHICLE_FOLDER, exist_ok=True)
os.makedirs(SUSPECT_FOLDER, exist_ok=True)
os.makedirs(os.path.join(PLATE_FOLDER, MOST_CLEARED_FOLDER), exist_ok=True)
os.makedirs(os.path.join(VEHICLE_FOLDER, MOST_CLEARED_FOLDER), exist_ok=True)

# Global flag for controlling threads
running = True
stop_queue = queue.Queue()

# Known license plates (add your actual plates here)
KNOWN_PLATES = ['MH20EE7602']


class LicensePlateRecognizer:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.last_plate = ""
        self.plate_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')
        if self.plate_cascade.empty():
            raise Exception("Failed to load Haar Cascade classifier")
        self.last_capture_time = 0

    def detect_license_plate(self, frame):
        """Detect license plate using Haar Cascade"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect plates with adjusted parameters
        plates = self.plate_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 30))

        return plates

    def save_images(self, frame, plate_roi):
        """Save full vehicle and plate images with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        # Save full vehicle image
        vehicle_path = os.path.join(VEHICLE_FOLDER, f"vehicle_{timestamp}.jpg")
        cv2.imwrite(vehicle_path, frame)

        # Save license plate image
        plate_path = os.path.join(PLATE_FOLDER, f"plate_{timestamp}.jpg")
        cv2.imwrite(plate_path, plate_roi)

        return vehicle_path, plate_path

    def process_frame(self, frame):
        """Process a single frame for license plate recognition"""
        # Detect license plates
        plates = self.detect_license_plate(frame)

        for (x, y, w, h) in plates:
            # Draw rectangle around plate
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Extract plate ROI
            plate_roi = frame[y:y+h, x:x+w]

            vehicle_path, plate_path = self.save_images(frame, plate_roi)

            print(f"Vehicle image saved: {vehicle_path}")
            print(f"Plate image saved: {plate_path}")

        return frame

    def license_plate_recognition(self):
        """Main function to run license plate recognition"""
        # Open video capture
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video capture")
            return

        try:
            while running:
                current_time = time.time()
                if current_time - self.last_capture_time >= CAPTURE_INTERVAL:
                    ret, frame = cap.read()
                    if not ret:
                        print("Error: Could not read frame")
                        break

                # Process frame
                    processed_frame = self.process_frame(frame)
                    self.last_capture_time = current_time
                else:
                    # Still read frame to keep video smooth, but don't process
                    ret, frame = cap.read()
                    if not ret:
                        print("Error: Could not read frame")
                        break
                    processed_frame = frame
                # Display result

                cv2.imshow('License Plate Recognition', processed_frame)

                # Exit on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    stop_queue.put("stop")
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def calculate_sharpness(self, image_path):
        """Calculate sharpness score using Laplacian variance"""
        image = cv2.imread(image_path)
        if image is None:
            return 0
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def get_clearest_image(self, folder_path):
        """Find the clearest image in a folder"""
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(
            ('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]

        if not image_files:
            print(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No images found in the folder.")
            return None

        sharpness_scores = []
        for img_file in image_files:
            img_path = os.path.join(folder_path, img_file)
            score = self.calculate_sharpness(img_path)
            sharpness_scores.append((img_file, score))

        # Sort by sharpness score (descending)
        sharpness_scores.sort(key=lambda x: x[1], reverse=True)

        return sharpness_scores[0][0]  # Return filename of clearest image

    def process_folder(self, input_folder):
        """Process a single folder: find clearest image, copy it, delete others"""
        # Validate folder exists
        if not os.path.isdir(input_folder):
            print(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error: The specified folder does not exist.")
            return

        # Create output folder if it doesn't exist
        output_folder = os.path.join(input_folder, MOST_CLEARED_FOLDER)
        os.makedirs(output_folder, exist_ok=True)

        # Find clearest image
        clearest_image = self.get_clearest_image(input_folder)

        if clearest_image:
            # Source and destination paths
            src_path = os.path.join(input_folder, clearest_image)
            dst_path = os.path.join(output_folder, clearest_image)

            # Copy the image (use copy2 to preserve metadata)
            shutil.copy2(src_path, dst_path)
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Copied clearest image '{clearest_image}' to '{output_folder}'")

            # Delete all source images except the clearest one
            image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
            for img_file in image_files:
                if img_file != clearest_image:
                    img_path = os.path.join(input_folder, img_file)
                    os.remove(img_path)
                    print(
                        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Deleted source image: '{img_file}'")
            img_path = os.path.join(input_folder, clearest_image)
            os.remove(img_path)
        else:
            print(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No valid images found to process.")

    def clear_folder_contents(self, folder_path):
        """Clear contents of a folder"""
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

    def clear_plates(self):
        """Monitor and process plate folder"""
        input_folder = os.path.abspath(PLATE_FOLDER).strip()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting plate image processing monitor...")
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Monitoring folder: {input_folder}")

        try:
            while running:
                self.process_folder(input_folder)
                # Reduced sleep time for more responsive processing
                time.sleep(5)
        except Exception as e:
            print(f"Error in clear_plates: {e}")
        finally:
            print("Plate processing stopped")

    def clear_vehicles(self):
        """Monitor and process vehicle folder"""
        input_folder = os.path.abspath(VEHICLE_FOLDER).strip()
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting vehicle image processing monitor...")
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Monitoring folder: {input_folder}")

        try:
            while running:
                self.process_folder(input_folder)
                # Reduced sleep time for more responsive processing
                time.sleep(5)
        except Exception as e:
            print(f"Error in clear_vehicles: {e}")
        finally:
            print("Vehicle processing stopped")

    def text_recognize(self):
        """Perform OCR on the clearest plate image"""
        folder_path = os.path.join(os.path.abspath(
            PLATE_FOLDER), MOST_CLEARED_FOLDER)
        result = []

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                image_path = os.path.join(folder_path, filename)
                result = self.reader.readtext(image_path, detail=0)
                os.remove(image_path)  # Remove after processing

        return result[0] if result else None

    def move_to_suspect(self):
        """Move vehicle images to suspect folder"""
        source_folder = os.path.join(os.path.abspath(
            VEHICLE_FOLDER), MOST_CLEARED_FOLDER)
        for filename in os.listdir(source_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                src_path = os.path.join(source_folder, filename)
                dst_path = os.path.join(
                    os.path.abspath(SUSPECT_FOLDER), filename)
                shutil.copy2(src_path, dst_path)

    def ocr_processing(self):
        """Main OCR processing loop"""
        print("OCR processing started")
        try:
            while running:
                result = self.text_recognize()

                if result is not None:
                    result = result.replace(" ", "")
                    result = re.sub(r'[^A-Z0-9]', '', result.upper())

                print("OCR result: ", result)

                if result is None:
                    print("No number plate detected")
                    # Clear both folders
                    self.clear_folder_contents(os.path.join(
                        PLATE_FOLDER, MOST_CLEARED_FOLDER))
                    self.clear_folder_contents(os.path.join(
                        VEHICLE_FOLDER, MOST_CLEARED_FOLDER))
                elif self.last_plate == "" or result != self.last_plate:
                    if result in KNOWN_PLATES:
                        print("Known number plate detected")
                        self.last_plate = result
                        # Clear both folders
                        self.clear_folder_contents(os.path.join(
                            PLATE_FOLDER, MOST_CLEARED_FOLDER))
                        self.clear_folder_contents(os.path.join(
                            VEHICLE_FOLDER, MOST_CLEARED_FOLDER))
                    else:
                        print("Unknown number plate detected")
                        self.last_plate = result
                        # Clear plate folder, move vehicle images to suspect
                        now = datetime.now()
                        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                        # Text to write
                        text_to_write = f"suspect vehicle {timestamp} is attemp to {result}\n"
                        # Open the text file in append mode and write
                        with open("log.txt", "a") as file:
                            file.write(text_to_write)
                        self.clear_folder_contents(os.path.join(
                            PLATE_FOLDER, MOST_CLEARED_FOLDER))
                        self.move_to_suspect()
                elif self.last_plate == result:
                    print("Same plate as before")
                    self.clear_folder_contents(os.path.join(
                        PLATE_FOLDER, MOST_CLEARED_FOLDER))
                    self.clear_folder_contents(os.path.join(
                        VEHICLE_FOLDER, MOST_CLEARED_FOLDER))

                # Reduced sleep time for more responsive processing
                time.sleep(5)
        except Exception as e:
            print(f"Error in OCR processing: {e}")
        finally:
            print("OCR processing stopped")


def monitor_input():
    """Monitor for 'stop' command"""
    global running
    while True:
        user_input = input().strip().lower()
        if user_input == "stop":
            running = False
            stop_queue.put("stop")
            break


def main():
    global running

    recognizer = LicensePlateRecognizer()

    # Start all processes in separate threads
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Start the license plate recognition
        lpr_future = executor.submit(recognizer.license_plate_recognition)

        # Start the folder monitors
        plates_future = executor.submit(recognizer.clear_plates)
        vehicles_future = executor.submit(recognizer.clear_vehicles)

        # Start the OCR processing
        ocr_future = executor.submit(recognizer.ocr_processing)

        # Start input monitoring
        input_future = executor.submit(monitor_input)

        # Wait for any of the processes to complete or stop command
        while running:
            try:
                # Check if any thread has raised an exception
                if lpr_future.done():
                    lpr_future.result()  # This will raise any exception that occurred
                if plates_future.done():
                    plates_future.result()
                if vehicles_future.done():
                    vehicles_future.result()
                if ocr_future.done():
                    ocr_future.result()
                if input_future.done():
                    input_future.result()
                    break

                # Check for stop command from other threads
                if not stop_queue.empty():
                    running = False
                    break

                time.sleep(1)
            except Exception as e:
                print(f"Error in main execution: {e}")
                running = False
                break

    print("Shutting down all processes...")

    # Clean up
    recognizer.clear_folder_contents(
        os.path.join(PLATE_FOLDER, MOST_CLEARED_FOLDER))
    recognizer.clear_folder_contents(
        os.path.join(VEHICLE_FOLDER, MOST_CLEARED_FOLDER))

    print("System shutdown complete")


if __name__ == "__main__":
    main()

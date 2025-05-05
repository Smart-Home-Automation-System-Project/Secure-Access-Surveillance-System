import cv2
import numpy as np
import os
import pytesseract
from datetime import datetime
import re

# Configure pytesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class LicensePlateRecognizer:
    def __init__(self, reference_plate=None):
        self.reference_plate = reference_plate
        self.output_dir = "output_plates"
        self.temp_dir = "temp_images"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

        # Initialize plate detector (using Haar cascade as example)
        self.plate_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')

    def preprocess_image(self, img):
        """Enhance image for better OCR results"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        return processed

    def detect_license_plate(self, frame):
        """Detect license plate in the frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = self.plate_cascade.detectMultiScale(gray, scaleFactor=1.1,
                                                     minNeighbors=5,
                                                     minSize=(100, 30))

        for (x, y, w, h) in plates:
            # Ensure we have a reasonable aspect ratio for license plates
            aspect_ratio = w / h
            if 2 < aspect_ratio < 6:
                plate_img = frame[y:y+h, x:x+w]
                return plate_img, (x, y, w, h)
        return None, None

    def extract_plate_number(self, plate_img):
        """Extract text from license plate image"""
        # Preprocess the license plate image
        processed = self.preprocess_image(plate_img)

        # Use Tesseract OCR to extract text
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        text = pytesseract.image_to_string(processed, config=custom_config)

        # Clean up the extracted text
        cleaned_text = re.sub(r'[^A-Z0-9]', '', text.upper())
        return cleaned_text

    def process_frame(self, frame):
        """Process each frame for license plate recognition"""
        plate_img, coords = self.detect_license_plate(frame)
        if plate_img is not None:
            # Save temporary images
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            plate_path = os.path.join(self.temp_dir, f"plate_{timestamp}.jpg")
            full_img_path = os.path.join(
                self.temp_dir, f"full_{timestamp}.jpg")

            cv2.imwrite(plate_path, plate_img)
            cv2.imwrite(full_img_path, frame)

            # Extract plate number
            plate_number = self.extract_plate_number(plate_img)
            print(f"Detected plate: {plate_number}")

            # Verify plate number
            if self.reference_plate and plate_number == self.reference_plate:
                print("YES - Plate matches reference")
                # Delete temporary images
                os.remove(plate_path)
                os.remove(full_img_path)
                return "YES", plate_number
            else:
                print("NO - Plate doesn't match or no reference provided")
                # Save to output directory
                output_plate_path = os.path.join(
                    self.output_dir, f"plate_{timestamp}.jpg")
                output_full_path = os.path.join(
                    self.output_dir, f"full_{timestamp}.jpg")
                os.rename(plate_path, output_plate_path)
                os.rename(full_img_path, output_full_path)
                return "NO", plate_number
        return None, None

    def clean_temp_files(self):
        """Clean up temporary files"""
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")


def main():
    # Initialize with a reference plate number (optional)
    reference_plate = "MH20EE7602"  # Set to None if you don't have a reference
    recognizer = LicensePlateRecognizer(reference_plate)

    # Initialize video capture (0 for webcam, or video file path)
    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process the frame
            status, plate_number = recognizer.process_frame(frame)

            # Display results
            cv2.imshow('License Plate Recognition', frame)

            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        recognizer.clean_temp_files()


if __name__ == "__main__":
    main()

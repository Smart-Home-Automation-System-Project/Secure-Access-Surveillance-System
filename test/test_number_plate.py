import unittest
import os
import numpy as np
import pytesseract
from number_plate import LicensePlateRecognizer

class TestLicensePlateRecognizer(unittest.TestCase):
    def setUp(self):
        self.recognizer = LicensePlateRecognizer()

    def test_preprocess_image(self):
        dummy_img = np.zeros((100, 200, 3), dtype=np.uint8)
        processed = self.recognizer.preprocess_image(dummy_img)
        self.assertIsNotNone(processed)

    def test_detect_license_plate_no_plate(self):
        dummy_img = np.zeros((500, 500, 3), dtype=np.uint8)
        plate_img, coords = self.recognizer.detect_license_plate(dummy_img)
        self.assertIsNone(plate_img)
        self.assertIsNone(coords)

    @unittest.skipUnless(os.path.exists(pytesseract.pytesseract.tesseract_cmd), "Tesseract not available")
    def test_extract_plate_number_blank(self):
        dummy_plate = np.zeros((50, 150, 3), dtype=np.uint8)
        plate_number = self.recognizer.extract_plate_number(dummy_plate)
        self.assertIsInstance(plate_number, str)

    def test_process_frame_no_plate(self):
        dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
        status, plate = self.recognizer.process_frame(dummy_img)
        self.assertIsNone(status)
        self.assertIsNone(plate)

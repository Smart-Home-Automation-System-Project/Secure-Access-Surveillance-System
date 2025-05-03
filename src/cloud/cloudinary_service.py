import cloudinary
import cloudinary.uploader
import os
from datetime import datetime
import cv2
import json
import uuid


class CloudinaryService:
    def __init__(self):
        # Load Cloudinary configuration
        try:
            with open("/Secure-Access-Surveillance-System/", "r") as f:
                CLOUDINARY_CONFIG = json.load(f)
        except FileNotFoundError:
            raise Exception("[ERROR] cloudinary_config.json not found!")

        cloudinary.config(
            cloud_name=CLOUDINARY_CONFIG['cloud_name'],
            api_key=CLOUDINARY_CONFIG['api_key'],
            api_secret=CLOUDINARY_CONFIG['api_secret']
        )
        self.local_dir = '../src/db/intruder_images'
        os.makedirs(self.local_dir, exist_ok=True)

    def upload_image(self, frame):
        """Upload image to Cloudinary"""
        image_name = f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        local_path = os.path.join(self.local_dir, f"{image_name}.jpg")
        try:
            # Save the image locally
            cv2.imwrite(local_path, frame)

            result = cloudinary.uploader.upload(
                local_path,
                public_id=image_name,
                folder="intruders"
            )
            # Clean up local file after upload
            if os.path.exists(local_path):
                os.remove(local_path)

            print(f"[INFO] Image uploaded to Cloudinary: {result['secure_url']}") #! DEBUGGING  
            return result['secure_url']
        except Exception as e:
            print(f"[ERROR] Failed to upload image: {e}")
            return local_path
            
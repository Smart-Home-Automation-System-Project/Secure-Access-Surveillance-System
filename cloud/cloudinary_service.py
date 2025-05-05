import cloudinary
import cloudinary.uploader
import os
from datetime import datetime
import cv2
import uuid
from dotenv import load_dotenv


class CloudinaryService:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Configure Cloudinary from environment variables
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        
        if not all([os.getenv('CLOUDINARY_CLOUD_NAME'), 
                  os.getenv('CLOUDINARY_API_KEY'), 
                  os.getenv('CLOUDINARY_API_SECRET')]):
            print("[WARNING] One or more Cloudinary environment variables are missing")

        self.local_dir = '../db/intruder_images'
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
            
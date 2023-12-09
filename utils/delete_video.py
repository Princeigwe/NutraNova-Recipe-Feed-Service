from dotenv import load_dotenv
import os
load_dotenv()


import cloudinary
import cloudinary.uploader


cloudinary.config(
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
  api_key = os.environ.get("CLOUDINARY_API_KEY"),
  api_secret = os.environ.get("CLOUDINARY_API_SECRET")
)

def delete_cloudinary_video_asset(public_id):
  cloudinary.uploader.destroy(public_id, resource_type='video')
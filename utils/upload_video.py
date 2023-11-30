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


def upload_video(file):
  response = cloudinary.uploader.upload_large(file,resource_type = "video", use_filename=True, unique_filename=False)
  return response
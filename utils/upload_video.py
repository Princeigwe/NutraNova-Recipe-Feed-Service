from dotenv import load_dotenv
import os
load_dotenv()


import cloudinary
import cloudinary.uploader
import cloudinary

cloudinary.config(
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
  api_key = os.environ.get("CLOUDINARY_API_KEY"),
  api_secret = os.environ.get("CLOUDINARY_API_SECRET")
)


def upload_video(file):
  response = cloudinary.uploader.upload_large(file,resource_type = "video", use_filename=True, unique_filename=False)
  return response


def upload_video_and_thumbnail(file):
  upload = upload_video(file)
  video_public_id = upload['public_id']
  thumbnail = cloudinary.CloudinaryVideo(video_public_id).image()
  return {
    "video": upload['secure_url'],
    "thumbnail": thumbnail
  }
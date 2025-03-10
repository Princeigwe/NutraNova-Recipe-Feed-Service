from django.urls import path
from .views import upload_recipe_image_to_cloudinary, upload_recipe_video_to_cloudinary, story_upload

urlpatterns = [
  path('upload/', upload_recipe_image_to_cloudinary, name='image-upload'),
  path('upload/video', upload_recipe_video_to_cloudinary, name='video-upload'),
  path('upload/story', story_upload, name='story-upload')
]
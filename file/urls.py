from django.urls import path
from .views import upload_recipe_image_to_cloudinary

urlpatterns = [
  path('upload/', upload_recipe_image_to_cloudinary, name='image-upload'),
]
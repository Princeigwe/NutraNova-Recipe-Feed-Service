from django.shortcuts import render
from utils.compress import compress_image
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from django.core.files.storage import FileSystemStorage
from utils.auth_decorator import is_authenticated
from rest_framework.exceptions import ParseError
from django.conf import settings
from utils.upload_image import upload_and_get_image_details
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# @csrf_exempt
# @is_authenticated
@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_recipe_image_to_cloudinary(request):
  recipe_images = []
  if request.FILES:
    # request.data.getlist(<key_name>) retrieve a list of values for a given key from the request data
    for image in request.data.getlist('images'):
      if any(char.isspace() for char in image.name):
        raise ParseError("Image names cannot be parsed, rename them without space characters.")
      
      default_storage = settings.MEDIA_ROOT
      fs = FileSystemStorage(location=default_storage)
      file = fs.save(image.name, image)
      file_url = fs.url(file) # /media/<image>

      image_path = f"{settings.BASE_DIR}{file_url}"

      #compress image and upload the compressed image
      compressed_image = compress_image(image_path)
      upload = upload_and_get_image_details(compressed_image)
      uploaded_image_url = upload['secure_url']
      recipe_images.append(uploaded_image_url)
      
    return Response(
      {
        "message": "Images uploaded",
        "images": recipe_images
        }
                    )
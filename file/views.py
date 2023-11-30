from django.shortcuts import render
from utils.compress import compress_image
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, renderer_classes
from django.core.files.storage import FileSystemStorage
from utils.request_authz import jwt_authorization
from rest_framework.exceptions import ParseError
from django.conf import settings
from utils.upload_image import upload_and_get_image_details
from django.views.decorators.csrf import csrf_exempt
from utils.upload_video import upload_video, upload_video_and_thumbnail

# Create your views here.

@csrf_exempt # ignore csrf_token error on file upload
@api_view(['POST'])
@jwt_authorization # calling the api_view decorator before the custom decorator is also a step in fixing rendering issue
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
      },
    )


@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_recipe_video_to_cloudinary(request):
  video = request.FILES['video'] if 'video' in request.FILES else None
  if video:
    if any( char.isspace() for char in video.name): # checking for gaps in the file name
      video.name = video.name.replace(' ', '_')
  
    default_storage = settings.MEDIA_ROOT
    fs = FileSystemStorage(location=default_storage)
    file = fs.save(video.name, video)
    file_url = fs.url(file)

    video_path = f"{settings.BASE_DIR}{file_url}"
    upload = upload_video_and_thumbnail(video_path)
    return Response(upload)
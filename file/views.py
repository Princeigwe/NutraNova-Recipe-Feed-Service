from django.shortcuts import render
from utils.compress import compress_image
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from django.core.files.storage import FileSystemStorage
from utils.request_authz import jwt_authorization
from rest_framework.exceptions import ParseError
from django.conf import settings
from utils.upload_image import upload_and_get_image_details
from django.views.decorators.csrf import csrf_exempt
from threads.upload_video_thread import UploadVideoThread
from utils.get_user import get_user_rest
from rest_framework import status
import os


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
        image.name = image.name.replace(' ', '_')
        print(image.name)
      
      default_storage = settings.MEDIA_ROOT
      fs = FileSystemStorage(location=default_storage)
      file = fs.save(image.name, image)
      file_url = fs.url(file) # /media/<image>

      image_path = f"{settings.BASE_DIR}{file_url}"

      if image_path.endswith(".png"):
        upload = upload_and_get_image_details(image_path)
        uploaded_image_url = upload['secure_url']
        recipe_images.append(uploaded_image_url)
      
      elif image_path.endswith(".jpg"):
        #compress image and upload the compressed image
        compressed_image = compress_image(image_path)
        upload = upload_and_get_image_details(compressed_image)
        uploaded_image_url = upload['secure_url']
        recipe_images.append(uploaded_image_url)
      
      else:
        # delete invalid file from media directory 
        os.remove(image_path)
        return Response(
          {"message": "invalid file format"},
          status=status.HTTP_400_BAD_REQUEST
        )


      # #compress image and upload the compressed image
      # compressed_image = compress_image(image_path)
      # upload = upload_and_get_image_details(compressed_image)
      # uploaded_image_url = upload['secure_url']
      # recipe_images.append(uploaded_image_url)

      # delete image from media directory after upload
      os.remove(image_path)
      print("recipe images:", recipe_images)

    return Response(
      {
        "message": "Images uploaded",
        "images": recipe_images
      },
    )


@api_view(['POST'])
@jwt_authorization
@parser_classes([MultiPartParser])
def upload_recipe_video_to_cloudinary(request):
  user = get_user_rest(request)
  video = request.FILES['video'] if 'video' in request.FILES else None
  if video:
    if any( char.isspace() for char in video.name): # checking for gaps in the file name
      video.name = video.name.replace(' ', '_')
  
    # default_storage = settings.MEDIA_ROOT
    # fs = FileSystemStorage(location=default_storage)
    fs = FileSystemStorage()
    file = fs.save(video.name, video)
    file_url = fs.url(file)

    video_path = f"{settings.BASE_DIR}{file_url}"

    # create extra thread to perform upload video operation on it
    upload_video_thread = UploadVideoThread(video_path)
    upload_video_thread.daemon = True # make thread daemonic
    upload_video_thread.start() # run thread
    upload_video_thread.join() # wait for daemonic thread to execute

    request.session[f"{user['email']}_recipe_video_detail"] = {
      "video": upload_video_thread.video,
      "thumbnail": upload_video_thread.thumbnail
    }

    # delete image from media directory after upload
    os.remove(video_path)

    # expire session in 20 minutes; in case not used
    request.session.set_expiry(1200)

    return Response( 
      {
        "message": "video uploaded", 
        "video": upload_video_thread.video,
        "thumbnail": upload_video_thread.thumbnail,
      }
    )

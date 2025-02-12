from django.shortcuts import render
from .mongo_database import database
from utils.get_user import get_user_rest
import datetime
import os
import base64
from PIL import Image
from django.conf import settings
import time


stories = database.recipe_stories
# Create your views here.


def upload_story(request, image_path):
  """
  this function is imported in the file module, which is primarily responsible for uploading media files.
  image path is gotten from the file module, and the image content is read as a binary file. This content is then
  saved in MongoDB, and the file is deleted from the code filesystem.
  """
  user = get_user_rest(request)

  #* SOLUTION ON HOW TO SAVE MEDIA FILES IN MONGODB AND EFFECTIVELY REPRESENT THAT DATA IN GRAPHQL DATA SCHEMA:
  #todo 1: when file is selected, convert to webp to reduce size and maintain quality.
  #todo 2: compress it further to 1mb to retain all data without loss when encoding.
  #todo 3: read the file buffer data and encode it in base64
  #todo 4: save the encoded string to mongodb with the attribute "base64_encoded"
  #todo 5: to represent this data in GraphQL schema, use the String data type
  if image_path.endswith(".jpg") or image_path.endswith(".jpeg") or image_path.endswith(".png"):

    default_media_path = settings.MEDIA_ROOT  # media directory
    image_name_without_extension = os.path.splitext(os.path.basename(image_path))[0]
    image = Image.open(image_path)
    image = image.convert('RGB')
    directed_path = f"{default_media_path}/" + f"{image_name_without_extension}" + ".webp"
    image.save(directed_path, "webp")

    image_size = os.path.getsize(directed_path)

    limit_size = 10485760 # 10MB

    # as long as the webp image is more than 5MB, compress it
    while image_size > limit_size:
      image = Image.open(image_path)
      width, height = image.size

      new_size = (width//2, height//2)
      resized_image = image.resize(new_size)
      
      # replacing the previous webp image with the compressed image
      resized_image.save(directed_path, 'WEBP', quality=90)

    file = open(directed_path, "rb")
    file_content = file.read()

    encoded_image = base64.b64encode(file_content).decode('utf-8')
    username = user['username']
    story = {
      "username": username,
      "encoded": encoded_image,
      "date": datetime.datetime.now(tz=datetime.timezone.utc)
    }
    story = stories.insert_one(story)
    
    # delete image files from media directory after upload
    os.remove(image_path)
    os.remove(directed_path)
  
  else:
    # deleting the invalid file
    os.remove(image_path)
    raise Exception("Invalid file type. Upload image")





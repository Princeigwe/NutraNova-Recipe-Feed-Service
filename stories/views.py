from django.shortcuts import render
from .mongo_database import database
from utils.request_authz import jwt_authorization
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import FileSystemStorage
from utils.get_user import get_user_rest
import datetime
import os


stories = database.recipe_stories

# Create your views here.


def upload_story(request, image_path):
  """
  this function is imported in the file module, which is primarily responsible for uploading media files.
  image path is gotten from the file module, and the image content is read as a binary file. This content is then
  saved in MongoDB, and the file is deleted from the code filesystem.
  """
  user = get_user_rest(request)
  file = open(image_path, "rb")
  file_content = file.read()
  username = user['username']
  story = {
    "username": username,
    "image": file_content,
    "date": datetime.datetime.now(tz=datetime.timezone.utc)
  }
  story = stories.insert_one(story)
  # delete image file from media directory after upload
  print("story path: ", image_path)
  os.remove(image_path)
  print(story)
  


def get_followings_stories(request):
  """get stories from the users that the current user is following"""
  pass


def get_following_single_story(request):
  """get a single story for a user that the current user is following"""
  pass


def get_my_stories(request):
  pass


def get_my_story(request):
  pass



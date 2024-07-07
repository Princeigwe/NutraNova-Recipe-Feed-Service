from django.shortcuts import render
from .mongo_database import database
from utils.request_authz import jwt_authorization
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import FileSystemStorage
from utils.get_user import get_user_rest
import datetime


stories = database.recipe_stories

# Create your views here.

# @api_view(['POST'])
# @jwt_authorization # calling the api_view decorator before the custom decorator is also a step in fixing rendering issue
# @parser_classes([MultiPartParser])
def upload_story(request):
  """this function is imported in the file module, which is primarily responsible for uploading media files"""
  user = get_user_rest(request)
  username = user['username']
  story = {
    "username": username,
    "image": "binary_data_here",
    "date": datetime.datetime.now(tz=datetime.timezone.utc)
  }
  story = stories.insert_one(story)
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



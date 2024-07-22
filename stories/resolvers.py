from .mongo_database import database
from utils.get_user import get_user
from utils.expired_stories import fetch_expired_stories



stories = database.recipe_stories


def get_followings_stories(_, info):
  """get stories from the users that the current user is following"""
  pass


def get_following_single_story(_, info):
  """get a single story for a user that the current user is following"""
  pass


def resolve_my_stories(_, info,):
  user = get_user(info)
  expired_stories = fetch_expired_stories()
  user_stories_response = []
  # fetching (non-expired) stories uploaded by the current logged in user
  user_stories = stories.find({'username': user['username']})
  for story in user_stories:
    if story not in expired_stories:
      user_stories_response.append(story)
  
  return user_stories_response


# def get_my_story(request):
#   pass

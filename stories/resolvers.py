from .mongo_database import database
from utils.get_user import get_user
from utils.expired_stories import fetch_expired_stories
from django.core.cache import cache
from utils.get_user import get_access_token
from utils.user_service_comm import fetch_user_followings


stories = database.recipe_stories


def resolve_followings_stories(_, info):
  """get stories from the users that the current user is following"""
  user = get_user(info)
  username = user['username'] ## for some reason, i couldn't get feed cache key before setting this variable. reminder: DO NOT DELETE.
  request = info.context['request']
  access_token = get_access_token(request)

  existing_user_followings_cache = cache.get( f"{user['username']}_followings" )
  if existing_user_followings_cache == None:
      print(f" {username} following cache does not exist")
      user_followings = fetch_user_followings(user['username'], access_token)
      print( user_followings['data']['userFollowing']['users'] )
      # print( user_followings)
      users = user_followings['data']['userFollowing']['users']
      user_followings_cache = cache.set( key=f"{user['username']}_followings", value=users, timeout=600 ) # cache timeout set to 600 seconds
  
  user_followings_cache = cache.get(f"{user['username']}_followings")

  if len(user_followings_cache) > 0:
    followings_stories = []
    for following in user_followings_cache:
      following_username = following['username']
      following_stories = stories.find({'username': following['username']})
      print("following stories: ", following_stories)

      followings_stories.append( { 'username': following_username, 'stories': following_stories } )
  
  return followings_stories



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

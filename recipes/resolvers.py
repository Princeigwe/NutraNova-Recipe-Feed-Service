from .models import Recipe, Tag, Chef, Like
from utils.get_user import get_user
import datetime
from django.forms.models import model_to_dict
from utils.nutritional_value import calculated_nutritional_value
from os.path import splitext, basename
from threads.delete_video_thread import DeleteVideoThread
from utils.user_service_comm import fetch_user_followings
from utils.get_user import get_access_token
from django.core.cache import cache
import asyncio
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import time
from threads.like_recipe_thread import LikeRecipeThread

# todo: do not add the database_sync_to_async decorator, since this function is not being resolved
def get_tag(name):
  try:
    recipe_tag = Tag.objects.get(name=name)
    return recipe_tag
  except Tag.DoesNotExist:
    raise Exception("Tag not recorded in NutraNova")

@database_sync_to_async
def resolve_recipe_tags(*_):
  """this function may be needed when the user needs to see the list af all available tags for recipe creation"""
  tags = Tag.objects.all()
  tag_list = [tag.name for tag in tags]
  return tag_list

@database_sync_to_async
def resolve_create_recipe(_, info, input: dict):
  """
  The `resolve_create_recipe` function creates a new recipe with the given input data and returns a
  response containing the created recipe details.

  :returns a dictionary with two keys: "message" and "recipe". The value of the "message" key is a
  string indicating that the recipe has been created and saved as a draft. The value of the "recipe"
  key is a dictionary containing the details of the created recipe, including its title, description,
  ingredients, instructions, preparation time, cooking time, servings, nutritional value
  """
  user = get_user(info)
  request = info.context['request']

  try:

    chef, created = Chef.objects.get_or_create(username=user['username'], first_name=user['first_name'], last_name=user['last_name'])
    title = input['title']
    description = input['description']
    ingredients = input['ingredients']
    instructions = input['instructions']

    nutritional_value = calculated_nutritional_value(ingredients)

    # creating instance of datetime.time for recipe preparation time based on the input given
    if ('hour' in input['preparation_time'] and 'second' in input['preparation_time']):
      preparation_time = datetime.time( input['preparation_time']['hour'], input['preparation_time']['minute'], input['preparation_time']['seconds'] )
    elif ('second' in input['preparation_time']):
      preparation_time = datetime.time( 0, input['preparation_time']['minute'], input['preparation_time']['seconds'] )
    else:
      preparation_time = datetime.time( 0, input['preparation_time']['minute'], 0)

    # creating instance of datetime.time for recipe cooking time based on the input given
    if ('hour' in input['cooking_time'] and 'second' in input['cooking_time']):
      cooking_time = datetime.time( input['cooking_time']['hour'], input['cooking_time']['minute'], input['cooking_time']['seconds'] )
    elif ('second' in input['preparation_time']):
      cooking_time = datetime.time( 0, input['cooking_time']['minute'], input['cooking_time']['seconds'] )
    else:
      cooking_time = datetime.time( 0, input['cooking_time']['minute'], 0)
    
    # video and thumbnail data can be given based on session data or input data
    recipe_video_session = request.session.get(f"{user['email']}_recipe_video_detail")
    # print(recipe_video_session)
    if('video' in input):
      video = input['video']
      print(video)
      if('thumbnail' in input):
        thumbnail = input['thumbnail']

    elif recipe_video_session:
      video = recipe_video_session['video']
      thumbnail = recipe_video_session['thumbnail']
      # if session is present nd used, delete session data
      del request.session[f"{user['email']}_recipe_video_detail"]

    if('thumbnail' in input and 'video' not in input):
      raise Exception("Video must be provided with thumbnail")

    servings = input['servings']
    images = input['images']

    recipe = Recipe.objects.create(
      title=title,
      description=description,
      ingredients=ingredients,
      instructions=instructions,
      preparation_time=preparation_time,
      cooking_time=cooking_time,
      servings=servings,
      nutritional_value=nutritional_value,
      images=images,
      # if video and thumbnail is defined in local scope
      video=video if 'video' in locals() else None,
      thumbnail=thumbnail if 'thumbnail' in locals() else None,
      chef=chef
    )

    for tag_name in input['tags']:
      tag = get_tag(tag_name)
      recipe.tags.add(tag)
    
    recipe.save()
    tags = recipe.tags.all() # fetch all tags associated to the recipe

    # using snake-cased keys because GraphQL camel-cased response keys were not getting data. Also changed in schema
    chef_details = {
      "username": recipe.chef.username,
			"first_name": recipe.chef.first_name,
			"last_name": recipe.chef.last_name
    }

    # convert all recipe instance keys, except for "tags" to dict keys and assign to recipe_response variable
    recipe_response = model_to_dict(recipe, exclude=['tags', 'created', 'published', 'chef']) 
    recipe_response_tags = [tag.name for tag in tags]
    recipe_response['tags'] = recipe_response_tags
    recipe_response['created'] = recipe.created
    recipe_response['published'] = recipe.published
    recipe_response['chef'] = chef_details

    return {
      "message": "Recipe created and saved as draft",
      "recipe": recipe_response
    }
  
  except ConnectionError as e:
    raise Exception(e)
  
  # key error on deleting session with non-existing key 
  except KeyError:
    return None


@database_sync_to_async
def resolve_edit_recipe(_, info, input):
  user = get_user(info)
  request = info.context['request']
  try:
    current_chef = Chef.objects.get(username=user['username'])
    recipe_id = input['id']
    existing_recipe = Recipe.objects.get(chef=current_chef, id=recipe_id)

    if existing_recipe.status == "PUBLISHED":
      raise Exception("Published recipe can no longer be edited")

    existing_recipe_video_url = existing_recipe.video
    existing_recipe_video_public_id = splitext(basename(existing_recipe_video_url))[0] if existing_recipe_video_url != None else None

    if('thumbnail' in input and 'video' not in input):
      raise Exception("Video must be provided with thumbnail")

    for key,value in input.items():
      if value is not None:
        if(len(value) != 0):
          setattr(existing_recipe, key, value)

    recipe_video_session = request.session.get(f"{user['email']}_recipe_video_detail")

    if ('video' not in input and recipe_video_session):
      existing_recipe.video = recipe_video_session['video']
      existing_recipe.thumbnail = recipe_video_session['thumbnail']
      # if session is present and used, delete session data
      del request.session[f"{user['email']}_recipe_video_detail"]

    existing_recipe.save()
    tags = existing_recipe.tags.all() # fetch all tags associated to the recipe
    new_recipe_video_url = existing_recipe.video
    new_recipe_video_public_id = splitext(basename(new_recipe_video_url))[0] if new_recipe_video_url != None else None

    chef_details = {
      "username": existing_recipe.chef.username,
			"first_name": existing_recipe.chef.first_name,
			"last_name": existing_recipe.chef.last_name
    }

    existing_recipe_response = model_to_dict(existing_recipe, exclude=['tags', 'created', 'published', 'chef']) 
    existing_recipe_response_tags = [tag.name for tag in tags]
    existing_recipe_response['tags'] = existing_recipe_response_tags
    existing_recipe_response['created'] = existing_recipe.created
    existing_recipe_response['published'] = existing_recipe.published
    existing_recipe_response['chef'] = chef_details

    if existing_recipe_video_public_id != new_recipe_video_public_id:
      delete_video_thread = DeleteVideoThread(existing_recipe_video_public_id)
      delete_video_thread.start()

    return {
      "message": "Recipe created and saved as draft",
      "recipe": existing_recipe_response
    }
  except Recipe.DoesNotExist as e:
    raise Exception(e)


# RECIPE FEED THOUGHT PROCESS:
# make an API request to the user service, in order to get the list of usernames of followings
# cache the result for 30 minutes
# select a random list of usernames from the result, and for each username, fetch the latest recipe created by the chef
# append each data to a response list and return it.
# cache the response for 15 minutes
# repeat from 1 and 2 when user makes another recipe feed request

@database_sync_to_async
def resolve_recipe_feed(_, info):
  """
  The `resolve_recipe_feed` function retrieves a user's recipe feed from the cache, and if it doesn't
  exist, it fetches the user's followings, retrieves the latest recipe from each following chef, and
  populates the feed with the recipes.
  """
  user = get_user(info)
  username = user['username'] ## for some reason, i couldn't get feed cache key before setting this variable. reminder: DO NOT DELETE.
  request = info.context['request']
  access_token = get_access_token(request)

  existing_feed_cache = cache.get(f"{username}recipe_feed")

  if existing_feed_cache == None:
    print(f"{username} existing recipe feed cache does not exist")

    existing_user_followings_cache = cache.get( f"{user['username']}_followings" )
    if existing_user_followings_cache == None:
      print(f" {username} following cache does not exist")
      user_followings = fetch_user_followings(user['username'], access_token)
      print( user_followings['data']['userFollowing']['users'] )
      # print( user_followings)
      users = user_followings['data']['userFollowing']['users']
      user_followings_cache = cache.set( key=f"{user['username']}_followings", value=users, timeout=120 ) # cache timeout set to 120 seconds
    

    user_followings_cache = cache.get(f"{user['username']}_followings")
    print(f" {username} following cache:", user_followings_cache)
    feed = []
    if len(user_followings_cache) == 0:
      return {
        "message": "Empty. Follow users to populate your feed."
      }
    else:
      for user in user_followings_cache:
        chef = Chef.objects.get(username=user['username'])
        try:
          chef_latest_recipe = model_to_dict(chef.recipes.filter(status='PUBLISHED').latest('published'), exclude=['created', 'published', 'chef'])
          chef_detail = {
            "username": chef.username,
            "first_name": chef.first_name,
            "last_name": chef.last_name
          }
          chef_latest_recipe['chef'] = chef_detail
          chef_latest_recipe['created'] = chef.recipes.latest('published').created
          chef_latest_recipe['published'] = chef.recipes.latest('published').published
          feed.append(chef_latest_recipe)
        except Recipe.DoesNotExist:
          pass
        
      cache_data = { "message": "Recipe feed", "feed": feed }
      cache.set( key=f"{username}recipe_feed", value= cache_data, timeout=180 )
      print(f"{username} feed cache created")

      return{
        "message": "Recipe feed" if len(feed) > 0 else "Feed empty at the moment, follow more chefs",
        "feed": feed
      }
  
  feed_cache = cache.get(f"{username}recipe_feed")
  print(f"data from existing {username} feed cache")
  
  return{
    "message": feed_cache['message'],
    "feed": feed_cache['feed']
  }


def resolve_single_recipe(_, info, pk):
  user = get_user(info)
  existing_single_recipe_cache = cache.get(f"{user['username']}_fetch_recipe{pk}")
  if existing_single_recipe_cache == None:
    try:
      recipe = Recipe.objects.get(pk=pk)
      if (recipe.status == "PUBLISHED"):
        cache.set(key=f"{user['username']}_fetch_recipe{pk}", value=recipe, timeout=60)
        print("single recipe cache set")
        return{
          "message": "Recipe",
          "recipe": recipe
        }
      else:
        return{ "message": "Forbidden request" }
    except Recipe.DoesNotExist:
      raise Exception("Recipe does not exist")
  
  single_recipe_cache = cache.get(f"{user['username']}_fetch_recipe{pk}")
  print("data from existing single recipe cache")
  return{
        "message": "Recipe",
        "recipe": single_recipe_cache
      }


@database_sync_to_async
def resolve_my_drafts(_, info):
  user = get_user(info)
  try:
    chef = Chef.objects.get(username=user['username']) 

    # recipe query gave the synchronous only operation error even when using the channels database_sync_to_async decorator.
    # wrapping it in list function, retrieved the recipes properly.
    # reference to: https://stackoverflow.com/questions/63149616/getting-synchronousonlyoperation-error-even-after-using-sync-to-async-in-django
    drafts = list(chef.recipes.filter(status='DRAFT')) 
    return drafts
  except Chef.DoesNotExist:
    raise Exception("Chef data does not exist")
  except Recipe.DoesNotExist:
    raise Exception("Recipe not found")


@database_sync_to_async
def resolve_draft(_, info, pk):
  user = get_user(info)
  try:
    chef = Chef.objects.get(username=user['username'])
    draft = chef.recipes.get(pk=pk, status="DRAFT")
    return draft
  
  except Chef.DoesNotExist:
    raise Exception("Chef data does not exist")
  except Recipe.DoesNotExist:
    raise Exception("Draft with not found")


@database_sync_to_async
def resolve_my_published_recipes(_, info):
  user = get_user(info)
  try:
    chef = Chef.objects.get(username=user['username'])
    published_recipes = list(chef.recipes.filter(status="PUBLISHED"))
    return published_recipes
  except Chef.DoesNotExist:
    raise Exception("Chef data does not exist")


@database_sync_to_async
async def single_recipe_sub_generator(_, info, pk):
  while True:
    await asyncio.sleep(2)
    try:
      recipe = await database_sync_to_async(Recipe.objects.get)(id=pk, status="PUBLISHED")
      chef = await database_sync_to_async(lambda: recipe.chef)()
      likes =  await database_sync_to_async(recipe.likes.count)()
      chef_details = {
        "username": chef.username,
        "first_name": chef.first_name,
        "last_name": chef.last_name
      }
      recipe_response = recipe.__dict__ # change recipe instance to dictionary
      recipe_response['chef'] = chef_details
      response = {
        "recipe": recipe_response,
        "likes": likes
      }
      yield response
    except Recipe.DoesNotExist as error:
      raise Exception(error)


def resolve_single_recipe_sub(response, obj, pk):
  return response


@database_sync_to_async
def resolve_like_recipe(_, info, pk):
  user = get_user(info)
  try:
    recipe = Recipe.objects.get(id=pk, status='PUBLISHED')
    like_recipe_thread = LikeRecipeThread(user, recipe)
    like_recipe_thread.start()
    return f"You liked the recipe by {recipe.chef.username}"
  
  except Recipe.DoesNotExist as error:
    raise Exception(error)

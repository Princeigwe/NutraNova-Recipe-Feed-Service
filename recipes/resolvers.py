from .models import Recipe, Tag, Chef, Like, Comment, SavedRecipe, UpVote, DownVote
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
from threads.kafka_graph_chef_vote_recipe_thread import GraphChefVoteRecipeThread
from threads.kafka_graph_chef_un_like_recipe_thread import GraphChefUnLikeRecipeThread
from threads.kafka_request_recommended_feed_thread import RequestRecommendedFeedThread
from utils.kafka.produce.create_neo_graph_nodes import send_graph_nodes_details
from utils.follow_chefs_recommendations import follow_chefs_recommendations_for_current_user
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from enums.choices import VoteType
from utils.calculate_new_recommended_feed import calculate_new_recommended_feed

#* get_user(info) function in resolver functions are called to facilitate authenticated requests, and get user details
#* Tag objects are created directly on PostgreSQL with PGAdmin. I dont think this should be so.
#* my brain is occupied at the moment to write an alternative

#!: do not add the database_sync_to_async decorator, since this function is not being resolved
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

    # limiting the number of recipe tags to 5
    if len(input['tags']) > 5:
      raise Exception("Recipe tags is limited to a number of 5")

    for tag_name in input['tags']:
      tag = get_tag(tag_name)
      recipe.tags.add(tag)
    
    recipe.save()
    tags = recipe.tags.all() # fetch all tags associated to the recipe

    # using snake-cased keys because GraphQL camel-cased response keys were not getting data. Also changed in schema
    chef_details = {
      "username": recipe.chef.username,
			"first_name": recipe.chef.first_name,
			"last_name": recipe.chef.last_name,
      "vote_strength": recipe.chef.vote_strength,
      "is_verified": recipe.chef.is_verified
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
			"last_name": existing_recipe.chef.last_name,
      "vote_strength": existing_recipe.chef.vote_strength,
      "is_verified": existing_recipe.chef.is_verified
    }

    chef_preferences = {
      "dietary_preference": user["dietary_preference"],
      "health_goal":        user["health_goal"],
      "allergens":          user["allergens"],
      "activity_level":     user["activity_level"],
      "cuisines":           user["cuisines"],
      "medical_conditions": user["medical_conditions"],
      "taste_preferences":  user["taste_preferences"]
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
    
    # send message to kafka if recipe status is 'PUBLISHED'
    if existing_recipe_response['status'] == 'PUBLISHED':
      kafka_message = {
      "chef_username": chef_details['username'],
      "chef_first_name": chef_details['first_name'],
      "chef_last_name": chef_details['last_name'],
      "chef_preferences": chef_preferences,
      "recipe_title": existing_recipe_response['title'],
      "recipe_description": existing_recipe_response['description'],
      "recipe_ingredients": existing_recipe_response['ingredients'],
      "recipe_instructions": existing_recipe_response['instructions'],
      "recipe_preparation_time": str(existing_recipe_response['preparation_time']),
      "recipe_cooking_time": str(existing_recipe_response['cooking_time']),
      "recipe_servings": existing_recipe_response['servings'],
      "recipe_nutritional_value": existing_recipe_response['nutritional_value'],
      "recipe_published": str(existing_recipe_response['published']),
      "tags": existing_recipe_response['tags']
    }

    send_graph_nodes_details(kafka_message)

    return {
      "message": "Recipe published",
      "recipe": existing_recipe_response
    }
  except Recipe.DoesNotExist as e:
    raise Exception(e)




@database_sync_to_async
def resolve_recipe_feed(_, info):
  """
  FEED ALGORITHM
  =========================================================================
  1. A recipe feed cache for the current user is fetched

  2. If it doesn't exist:
      a. The cache for the followings of the user is fetched
      b. The user's following cache doesn't exist:
        b1. The followings of the current user is fetched from the users-microservice, 
            and the followings cache is created with a timeout of 600seconds
      c. The followings list of current user is retrieved from the followings cache
      d. If there are zero followings:
        d1. A request is sent to the recommendations microservice to recommend chefs to follow, 
            based on the dieting preferences of the current user. The user can now follow with the 
            "followUser" GraphQL resolver.

            else, if there are one or more followings:
              The latest recipe from each followings is fetched. 
              (There's plan to change from fetching single latest recipe to fetching 2 or 3 latest recipes from each chef)
        d2. Each recipe is added to a "feed" list that will be used to display a feed response to the current user.
      e. A recommendation's feed cache (its timeout = 300 seconds) that holds the calculated recommendations content
          from the recommendations service is fetched.
      f. If it doesn't exist, nothing happens. If it exists:
        f1. Recipes ins the recipe microservices are fetched based on the content of the recommendations cache.
        f2. These fetched recommended recipes are then added to the "feed" list to populate the user feed response.
      g. The recipe feed cache is created with the value of the "feed" list with a timeout of 250 seconds.

  3. If the recipe feed cache exists, its data is retrieved for feed response

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
      user_followings_cache = cache.set( key=f"{user['username']}_followings", value=users, timeout=600 ) # cache timeout set to 600 seconds
    

    user_followings_cache = cache.get(f"{user['username']}_followings")
    print(f" {username} following cache:", user_followings_cache)
    feed = []
    if len(user_followings_cache) == 0:
      chef_suggestions = follow_chefs_recommendations_for_current_user(info)
      return {
        "message": "Empty. Follow chefs to populate your feed.",
        "suggestions": chef_suggestions
      }
    else:
      for user in user_followings_cache:
        chef = Chef.objects.get(username=user['username'])
        try:
          # todo: edit this to fetch 3 or more latest recipes from each chef in in following_cache
          chef_latest_recipe = model_to_dict(chef.recipes.filter(status='PUBLISHED').latest('published'), exclude=['created', 'published', 'chef', 'tags'])
          chef_detail = {
            "username": chef.username,
            "first_name": chef.first_name,
            "last_name": chef.last_name,
            "is_verified": chef.is_verified
          }
          chef_latest_recipe['chef'] = chef_detail
          chef_latest_recipe['tags'] = chef.recipes.latest('published').tags.all().values_list('name', flat=True)
          chef_latest_recipe['created'] = chef.recipes.latest('published').created
          chef_latest_recipe['published'] = chef.recipes.latest('published').published
          feed.append(chef_latest_recipe)
        except Recipe.DoesNotExist:
          pass
        
      # adding recommendations from recommendation microservice to feed
      recommendations = cache.get(f"{username}_recommendation_feed")
      print("recommendations feed: ", recommendations)
      if not recommendations:
        pass
      else:
        print("Recommendations cache exist")
        for item in recommendations:
          recipe = Recipe.objects.get(title=item['recipe_title'], published=item['recipe_published_date'])
          chef = recipe.chef
          chef_details = {
            "username": chef.username,
            "first_name": chef.first_name,
            "last_name": chef.last_name,
            "is_verified": chef.is_verified
          }
          recipe_response = model_to_dict(recipe, exclude=['tags', 'created', 'published', 'chef']) # change recipe instance to dictionary
          recipe_response['chef'] = chef_details
          # selecting only the name attributes of each recipe Tag object
          recipe_response['tags'] = recipe.tags.all().values_list('name', flat=True)
          recipe_response['created'] = recipe.created
          recipe_response['published'] = recipe.published
          feed.append(recipe_response)

      # setting cache for next response in request when there is a cache-miss
      cache_data = { 
        "message": "Recipe feed" if len(feed) > 0 else "Feed empty at the moment, follow more chefs", 
        "feed": feed,
        "suggestions": None if len(feed) > 0 else follow_chefs_recommendations_for_current_user(info) 
      }
      cache.set( key=f"{username}recipe_feed", value= cache_data, timeout=250 )
      print(f"{username} feed cache created")

      # if there is a no feed cache, this is returned in response
      feed_cache = cache.get(f"{username}recipe_feed")
      return{
        "message": feed_cache['message'],
        "feed": feed_cache['feed'],
        "suggestions": feed_cache['suggestions']
      }
      # return{
      #   "message": "Recipe feed" if len(feed) > 0 else "Feed empty at the moment, follow more chefs",
      #   "feed": feed,
      #   "suggestions": None if len(feed) > 0 else follow_chefs_recommendations_for_current_user(info) 
      # }
  
  feed_cache = cache.get(f"{username}recipe_feed")
  print(f"data from existing {username} feed cache")
  
  return{
    "message": feed_cache['message'],
    "feed": feed_cache['feed'],
    "suggestions": feed_cache['suggestions']
  }


@database_sync_to_async
def resolve_my_drafts(_, info):
  user = get_user(info)
  try:
    chef = Chef.objects.get(username=user['username']) 

    drafts_responses = []
    # retrieve all tags manay-to-many field for draft in a single fetch 
    recipe_drafts = chef.recipes.filter(status='DRAFT').prefetch_related('tags')
    for draft in recipe_drafts:
      draft_response = model_to_dict(draft, exclude=['tags', 'created', 'published', 'chef'])
      chef_details = {
            "username": chef.username,
            "first_name": chef.first_name,
            "last_name": chef.last_name
          }
      draft_response['tags'] = [tag.name for tag in draft.tags.all()]
      draft_response['created'] = draft.created
      draft_response['published'] = draft.published
      draft_response['chef'] = chef_details

      drafts_responses.append(draft_response)
    return drafts_responses

    #* not sure this comment is necessary anymore, but I'll leave it
    # recipe query gave the synchronous only operation error even when using the channels database_sync_to_async decorator.
    # wrapping it in list function, retrieved the recipes properly.
    # reference to: https://stackoverflow.com/questions/63149616/getting-synchronousonlyoperation-error-even-after-using-sync-to-async-in-django

  except Chef.DoesNotExist:
    raise Exception("Chef data does not exist")
  except Recipe.DoesNotExist:
    raise Exception("Recipe not found")


@database_sync_to_async
def resolve_draft(_, info, pk):
  user = get_user(info)
  try:
    chef = Chef.objects.get(username=user['username'])
    recipe_draft = chef.recipes.get(pk=pk, status='DRAFT')
    draft_response = model_to_dict(recipe_draft, exclude=['tags', 'created', 'published', 'chef'])
    chef_details = {
      "username": chef.username,
      "first_name": chef.first_name,
      "last_name": chef.last_name
    }
    draft_response['tags'] = [tag.name for tag in recipe_draft.tags.all()]
    draft_response['created'] = recipe_draft.created
    draft_response['published'] = recipe_draft.published
    draft_response['chef'] = chef_details
    return draft_response
  
  except Chef.DoesNotExist:
    raise Exception("Chef data does not exist")
  except Recipe.DoesNotExist:
    raise Exception("Draft with not found")


@database_sync_to_async
def resolve_my_published_recipes(_, info):
  user = get_user(info)
  try:
    chef = Chef.objects.get(username=user['username'])
    # published_recipes = list(chef.recipes.filter(status="PUBLISHED"))
    # return published_recipes

    published_responses = []
    # retrieve all tags manay-to-many field for draft in a single fetch 
    recipes_published = chef.recipes.filter(status='PUBLISHED').prefetch_related('tags')
    for recipe in recipes_published:
      published_recipe_response = model_to_dict(recipe, exclude=['tags', 'created', 'published', 'chef'])
      chef_details = {
            "username": chef.username,
            "first_name": chef.first_name,
            "last_name": chef.last_name
          }
      published_recipe_response['tags'] = [tag.name for tag in recipe.tags.all()]
      published_recipe_response['created'] = recipe.created
      published_recipe_response['published'] = recipe.published
      published_recipe_response['chef'] = chef_details

      published_responses.append(published_recipe_response)
    return published_responses
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

      number_of_up_votes = await database_sync_to_async(recipe.upVotes.count)()
      recipe_up_votes = await database_sync_to_async(recipe.upVotes.all)()
      up_voters = [recipe_up_vote.voter for recipe_up_vote in recipe_up_votes]
      # making this unique for voters with vote_strength > 1.
      unique_up_voters = list(set(up_voters))

      number_of_down_votes = await database_sync_to_async(recipe.downVotes.count)()
      recipe_down_votes = await database_sync_to_async(recipe.downVotes.all)()
      down_voters = [recipe_down_vote.voter for recipe_down_vote in recipe_down_votes]
      unique_down_voters = list(set(down_voters))


      chef_details = {
        "username": chef.username,
        "first_name": chef.first_name,
        "last_name": chef.last_name,
        "vote_strength": chef.vote_strength,
        "is_verified": chef.is_verified
      }
      recipe_response = model_to_dict(recipe, exclude=['tags', 'created', 'published', 'chef'])
      recipe_response['chef'] = chef_details
      # selecting only the name attributes of each recipe Tag object
      recipe_response['tags'] = recipe.tags.all().values_list('name', flat=True)
      recipe_response['created'] = await database_sync_to_async(lambda: recipe.created)()
      recipe_response['published'] = await database_sync_to_async(lambda: recipe.published)()
      recipe_response['chef'] = chef_details
      response = {
        "recipe": recipe_response,
        "likes": likes,
        "up_votes": number_of_up_votes,
        "up_voters": unique_up_voters,
        "down_votes": number_of_down_votes,
        "down_voters": unique_down_voters
      }
      yield response
    except Recipe.DoesNotExist as error:
      raise Exception(error)


def resolve_single_recipe_sub(response, obj, pk):
  return response



# todo: add code for vote cache count that will be used in calculating when to fetch feed, just like in the resolve_like_recipe function
def resolve_up_vote_recipe(_, info, pk):
  user = get_user(info)
  request = info.context['request']

  try:
    recipe = Recipe.objects.get(id=pk, status='PUBLISHED')
    # getting or creating new chef objects
    # the object creation is implemented because the current user may be a new user who
    # starts voting recipes without creating or publishing recipes
    # voter = Chef.objects.get(username=user['username'], first_name=user['first_name'], last_name=user['last_name'], vote_strength=user['vote_strength'], is_verified=user['is_verified'])
    voter, created = Chef.objects.get_or_create(username=user['username'], first_name=user['first_name'], last_name=user['last_name'], vote_strength=user['vote_strength'], is_verified=user['is_verified'])
    voter_up_votes_count = UpVote.objects.filter(voter=voter, recipe=recipe).count()  # counting existing upVotes by current user on a recipe 
    voter_down_votes_count = DownVote.objects.filter(voter=voter, recipe=recipe).count()  # counting existing downVotes by current user on a recipe
    if (voter_up_votes_count == 0 and voter_down_votes_count == 0):
      up_vote_objects = []
      for i in range(voter.vote_strength):
        up_vote_objects.append( UpVote(voter=voter, recipe=recipe) ) # creating new Upvote objects here
      UpVote.objects.bulk_create(up_vote_objects) # saving the objects

      calculate_new_recommended_feed(request, user)

      voter_preferences = {
        "dietary_preference": user["dietary_preference"],
        "health_goal":        user["health_goal"],
        "allergens":          user["allergens"],
        "activity_level":     user["activity_level"],
        "cuisines":           user["cuisines"],
        "medical_conditions": user["medical_conditions"],
        "taste_preferences":  user["taste_preferences"]
      }
      # send message to kafka
      kafka_message = {
        "voter_username": user['username'],
        "voter_first_name": user['first_name'],
        "voter_last_name": user['last_name'],
        "voter_preferences": voter_preferences,
        "vote_type": VoteType.UP_VOTED.value,
        "recipe_title": recipe.title,
        "recipe_published": str(recipe.published),
      }

      # sending kafka message in background thread to create chef-to-recipe :UPVOTE relationship in recommendations microservice
      graph_chef_like_recipe_thread = GraphChefVoteRecipeThread(kafka_message)
      graph_chef_like_recipe_thread.start()
      
      return f"Your vote strength ( {voter.vote_strength} ), has been casted for this recipe."
    else:
      raise Exception("You have casted your vote already.")
  except Recipe.DoesNotExist:
    raise Exception("Recipe does not exist")
  except Chef.DoesNotExist:
    raise Exception("Chef does not exist")


def resolve_down_vote_recipe(_, info, pk):
  user = get_user(info)
  request = info.context['request']

  try:
    recipe = Recipe.objects.get(id=pk, status='PUBLISHED')
    # getting or creating new chef objects
    # the object creation is implemented because the current user may be a new user who
    # starts voting recipes without creating or publishing recipes
    # voter = Chef.objects.get(username=user['username'], first_name=user['first_name'], last_name=user['last_name'])
    voter, created = Chef.objects.get_or_create(username=user['username'], first_name=user['first_name'], last_name=user['last_name'], vote_strength=user['vote_strength'], is_verified=user['is_verified'])
    voter_up_votes_count = UpVote.objects.filter(voter=voter, recipe=recipe).count()  # counting existing upVotes by current user on a recipe 
    voter_down_votes_count = DownVote.objects.filter(voter=voter, recipe=recipe).count()  # counting existing downVotes by current user on a recipe
    if (voter_up_votes_count == 0 and voter_down_votes_count == 0):
      down_vote_objects = []
      for i in range(voter.vote_strength):
        down_vote_objects.append( DownVote(voter=voter, recipe=recipe) ) # creating new Upvote objects here
      DownVote.objects.bulk_create(down_vote_objects) # saving the objects

      calculate_new_recommended_feed(request, user)

      voter_preferences = {
        "dietary_preference": user["dietary_preference"],
        "health_goal":        user["health_goal"],
        "allergens":          user["allergens"],
        "activity_level":     user["activity_level"],
        "cuisines":           user["cuisines"],
        "medical_conditions": user["medical_conditions"],
        "taste_preferences":  user["taste_preferences"]
      }
      # send message to kafka
      kafka_message = {
        "voter_username": user['username'],
        "voter_first_name": user['first_name'],
        "voter_last_name": user['last_name'],
        "voter_preferences": voter_preferences,
        "vote_type": VoteType.DOWN_VOTED.value,
        "recipe_title": recipe.title,
        "recipe_published": str(recipe.published),
      }

      # sending kafka message in background thread to create chef-to-recipe :UPVOTE relationship in recommendations microservice
      graph_chef_like_recipe_thread = GraphChefVoteRecipeThread(kafka_message)
      graph_chef_like_recipe_thread.start()
      return f"Your vote strength ( {voter.vote_strength} ), has been casted for this recipe."
    else:
      raise Exception("You have casted your vote already")
  except Recipe.DoesNotExist:
    raise Exception("Recipe does not exist")
  except Chef.DoesNotExist:
    raise Exception("Chef does not exist")


@database_sync_to_async
def resolve_delete_recipe(_, info, pk):
  user = get_user(info)
  try:
    chef = Chef.objects.get(username=user['username'])
    recipe = Recipe.objects.get(id=pk, chef=chef)
    recipe.delete()
    return f"You deleted your recipe: {recipe.title}"
  except Recipe.DoesNotExist as error:
    raise Exception(error)


def resolve_search(_, info, query):
  """search functionality for recipes"""
  get_user(info)
  search_query = SearchQuery(query, search_type='plain')
  search_vector = SearchVector('title', 'description')
  recipes = Recipe.objects.annotate(
      search=search_vector,
      rank=SearchRank(search_vector, search_query)
  ).filter(search=search_query, status="PUBLISHED").order_by("-rank")
  total_recipes = recipes.count()
  results = []
  for recipe in recipes:
    chef_details = {
      "username": recipe.chef.username,
      "first_name": recipe.chef.first_name,
      "last_name": recipe.chef.last_name
    }
    recipe_response = model_to_dict(recipe, exclude=['tags', 'created', 'published', 'chef'])
    recipe_response['tags'] = recipe.tags.all().values_list('name', flat=True)
    recipe_response['created'] = recipe.created
    recipe_response['published'] = recipe.published
    recipe_response['chef'] = chef_details
    results.append(recipe_response)

  return{
      "message": "No results found for the given query." if total_recipes == 0 else "Results.",
      "results": results
  }


def resolve_comment_on_recipe(_, info, input: dict):
  user = get_user(info)
  try:
    recipe = Recipe.objects.get(id=input['id'], status="PUBLISHED")
    writer = Chef.objects.get(username=user['username'])
    comment = Comment.objects.create(
      writer = writer,
      recipe = recipe,
      content = input['content']
    )
    comment.save()
    return {
      "message": "Comment published.",
      "comment": comment
    }
  except Recipe.DoesNotExist:
    raise Exception("Recipe does not exist")


def resolve_recipe_comments(_, info, pk):
  get_user(info)
  try:
    recipe = Recipe.objects.get(id=pk, status="PUBLISHED")
    comments = recipe.comments.all()
    return{
      "message": "Recipe comments",
      "comments": comments
    }
  except Recipe.DoesNotExist:
    raise Exception("Recipe does not exist")


def resolve_comment_on_comment(_, info, input: dict):
  user = get_user(info)
  try:
    parent_comment = Comment.objects.get(id=input['id'])
    writer = Chef.objects.get(username=user['username'])
    child_comment = Comment.objects.create(
      writer = writer,
      parent_comment = parent_comment,
      content = input['content']
    )
    child_comment.save()
    return {
      "message": "Comment published.",
      "comment": child_comment
    }
  except Comment.DoesNotExist:
    raise Exception("Comment does not exist")


def resolve_comment_replies(_, info, pk):
  get_user(info)
  try:
    parent_comment = Comment.objects.get(id=pk)
    child_comments = parent_comment.replies.all()
    return {
      "message": "Comment replies",
      "comments": child_comments
    }
  except Comment.DoesNotExist:
    raise("Comment does not exist")


def resolve_save_for_later(_, info, pk):
  user = get_user(info)
  try:
    chef = Chef.objects.get(username=user['username']) # chef here is the current logged in user
    recipe = Recipe.objects.get(id=pk, status="PUBLISHED")
    SavedRecipe.objects.get(chef=chef, recipe=recipe)
    return "Recipe saved"
  except SavedRecipe.DoesNotExist:
    save_recipe = SavedRecipe.objects.create(chef=chef, recipe=recipe)
    save_recipe.save()
    return "Recipe saved"
  except Recipe.DoesNotExist:
    raise Exception("Recipe does not exist")


def resolve_my_saved_recipes(_, info):
  user = get_user(info)
  chef = Chef.objects.get(username=user['username']) # chef here is the current logged in user
  saved_recipes = SavedRecipe.objects.select_related('recipe').filter(chef=chef)
  recipes_response = []
  for save in saved_recipes:
    recipe = model_to_dict(save.recipe, exclude=['tags', 'created', 'published', 'chef'])
    chef_detail = {
      "username": save.recipe.chef.username,
      "first_name": save.recipe.chef.first_name,
      "last_name": save.recipe.chef.last_name
    }
    recipe['tags'] = save.recipe.tags.all().values_list('name', flat=True)
    recipe['chef'] = chef_detail
    recipe['created'] = save.recipe.created
    recipe['published'] = save.recipe.published

    recipes_response.append(recipe)

  return recipes_response
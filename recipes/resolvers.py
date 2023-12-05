from .models import Recipe, Tag, Chef
from utils.get_user import get_user
import datetime
from django.forms.models import model_to_dict
from utils.nutritional_value import calculated_nutritional_value


def get_tag(name):
  try:
    recipe_tag = Tag.objects.get(name=name)
    return recipe_tag
  except Tag.DoesNotExist:
    raise Exception("Tag not recorded in NutraNova")

def resolve_recipe_tags(*_):
  """this function may be needed when the user needs to see the list af all available tags for recipe creation"""
  tags = Tag.objects.all()
  tag_list = [tag.name for tag in tags]
  return tag_list


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
    return{
      "error": e
    }
  
  # key error on deleting session with non-existing key 
  except KeyError:
    return None


def resolve_edit_recipe(_, info, input):
  user = get_user(info)
  request = info.context['request']
  try:
    current_chef = Chef.objects.get(username=user['username'])
    recipe_id = input['id']
    existing_recipe = Recipe.objects.get(chef=current_chef, id=recipe_id)

    for key,value in input.items():
      if value is not None:
        if(len(value) != 0):
          setattr(existing_recipe, key, value)

    existing_recipe.save()
    tags = existing_recipe.tags.all() # fetch all tags associated to the recipe

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

    return {
      "message": "Recipe created and saved as draft",
      "recipe": existing_recipe_response
    }
  except Recipe.DoesNotExist as e:
    return{
      "error": e
    }

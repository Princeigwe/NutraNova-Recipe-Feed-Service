from .models import Recipe, Tag
from utils.get_user import get_user
import datetime
from django.forms.models import model_to_dict


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
  user = get_user(info)

  try:
    title = input['title']
    description = input['description']
    ingredients = input['ingredients']
    instructions = input['instructions']

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
      images=images,
      chef=user
    )

    for tag_name in input['tags']:
      tag = get_tag(tag_name)
      recipe.tags.add(tag)
    
    recipe.save()
    tags = recipe.tags.all() # fetch all tags associated to the recipe

    print(recipe.created)
    
    # convert all recipe instance keys, except for "tags" to dict keys and assign to recipe_response variable
    recipe_response = model_to_dict(recipe, exclude=['tags', 'created', 'published']) 
    recipe_response_tags = [tag.name for tag in tags]
    recipe_response['tags'] = recipe_response_tags
    recipe_response['created'] = recipe.created
    recipe_response['published'] = recipe.published

    return {
      "message": "Recipe created and saved as draft",
      "recipe": recipe_response
    }
  
  except ConnectionError as e:
    return{
      "error": e
    }


def publish_recipe(_, info, publish: bool):
  pass
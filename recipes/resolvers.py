from .models import Recipe
from utils.get_user import get_user
import datetime



def resolve_create_recipe(_, info, input: dict):
  user = get_user(info)

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
  recipe.save()

  return {
    "message": "Recipe created and saved as draft",
    "recipe": recipe
  }


def publish_recipe(_, info, publish: bool):
  pass
import os
from dotenv import load_dotenv
load_dotenv()
import requests

def get_recipe_ingredients(ingredients):
  list_of_ingredients = []
  for ingredient in ingredients:
    if "unit" in ingredient:
      calculated_ingredient = f"{ingredient['quantity']} {ingredient['unit']} {ingredient['name']}"
      list_of_ingredients.append(calculated_ingredient)
    else:
      calculated_ingredient = f"{ingredient['quantity']} {ingredient['name']}"
      list_of_ingredients.append(calculated_ingredient)

  # query will be used to get nutritional value of ingredients using the 
  query = ', '.join(list_of_ingredients)
  return query



def get_nutritional_value(ingredients):
  query = get_recipe_ingredients(ingredients)
  url = f"https://api.calorieninjas.com/v1/nutrition?query={query}"
  headers={'X-Api-Key': os.environ.get('CALORIES_NINJA_API_KEY')}
  response = requests.get(url, headers=headers)

  if response.status_code == requests.codes.ok:
    return response.json()
  else:
    print("Error:", response.status_code, response.text)


def calculated_nutritional_value(ingredients):
  ingredients_nutritional_values = get_nutritional_value(ingredients)

  # the list of all needed nutritional value from each ingredients
  nutrition_calories        = [ item['calories'] for item in ingredients_nutritional_values['items'] ]
  nutrition_fat             = [ item['fat_total_g'] for item in ingredients_nutritional_values['items'] ]
  nutrition_cholesterol     = [ item['cholesterol_mg'] for item in ingredients_nutritional_values['items'] ]
  nutrition_sodium          = [ item['sodium_mg'] for item in ingredients_nutritional_values['items'] ]
  nutrition_carbohydrates   = [ item['carbohydrates_total_g'] for item in ingredients_nutritional_values['items'] ]
  nutrition_fiber           = [ item['fiber_g'] for item in ingredients_nutritional_values['items'] ]
  nutrition_sugar           = [ item['sugar_g'] for item in ingredients_nutritional_values['items'] ]
  nutrition_protein         = [ item['protein_g'] for item in ingredients_nutritional_values['items'] ]
  nutrition_potassium       = [ item['potassium_mg'] for item in ingredients_nutritional_values['items'] ]

  # sum of each nutrient in ingredients
  total_calories = sum(nutrition_calories)
  total_fat = sum(nutrition_fat)
  total_cholesterol = sum(nutrition_cholesterol)
  total_sodium = sum(nutrition_sodium)
  total_carbohydrates = sum(nutrition_carbohydrates)
  total_fiber = sum(nutrition_fiber)
  total_sugar = sum(nutrition_sugar)
  total_protein = sum(nutrition_protein)
  total_potassium = sum(nutrition_potassium)

  nutritional_value = {
    "calories": total_calories,
    "fat": f"{total_fat}g",
    "cholesterol": f"{total_cholesterol}mg",
    "sodium": f"{total_sodium}mg",
    "carbohydrates": f"{total_carbohydrates}g",
    "fiber": f"{total_fiber}g",
    "sugar": f"{total_sugar}g",
    "protein": f"{total_protein}g",
    "potassium": f"{total_potassium}mg"
  }

  return nutritional_value
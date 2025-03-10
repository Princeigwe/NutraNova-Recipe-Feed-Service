from utils.get_user import get_access_token
from utils.recommendation_service_comm import fetch_recommended_recipes
from recipes.models import Recipe
from datetime import datetime


def follow_chefs_recommendations_for_current_user(info):
  # request for recipes fitting the user's preferences from the recommendations microservice
  request = info.context['request']
  access_token = get_access_token(request)
  recommendation_response = fetch_recommended_recipes(access_token)
  print(recommendation_response)
  recommendations = recommendation_response['data']['recommendFeedForNewUser']
  print("Recommendations fetched from recommendations microservice: ",recommendations)

  suggested_chefs = []
  for item in recommendations:
    recipe = Recipe.objects.get(title=item['recipe_title'], published=item['recipe_published_date'])
    chef = recipe.chef
    suggested_chefs.append(chef.username)

  suggested_chefs
  # creating a list of unique chef items
  suggested_chefs = list(set(suggested_chefs))
  return suggested_chefs

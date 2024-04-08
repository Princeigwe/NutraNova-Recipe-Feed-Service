import requests
import json

def fetch_recommended_recipes(access_token):
  try:
    recommendation_service_api_endpoint = "http://127.0.0.1:4000/graphql/"
    headers = { "Authorization": f"Bearer {access_token}", 'Content-Type': 'application/json' }

    query = f"""
            query RecommendRecipes {{
                recommendFeedForNewUser{{
                    recipe_title
                    recipe_published_date
                }}
            }}
            """
    response = requests.post( 
      recommendation_service_api_endpoint, 
      headers=headers,
      data= json.dumps( {
        "query": query,
        "operationName": "RecommendRecipes"
      } )
    )
    return response.json()
  except requests.exceptions.ConnectionError as e:
    print ("Error Connecting:",e)
  except requests.exceptions.Timeout as e:
    print ("Timeout Error:",e)
  except requests.exceptions.RequestException as e:
    print ("Something went wrong:",e)

import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

def fetch_recommended_recipes(access_token):
  try:
    recommendation_service_api_endpoint = os.environ.get('RECOMMENDATION_SERVICE_API_ENDPOINT')
    print("recommendations service endpoint: ", recommendation_service_api_endpoint)
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
      json={"query": query}
    )
    print("response text from recommendations service: ", response.text)
    return response.json()
  except requests.exceptions.ConnectionError as e:
    print ("Error Connecting:",e)
  except requests.exceptions.Timeout as e:
    print ("Timeout Error:",e)
  except requests.exceptions.RequestException as e:
    print ("Something went wrong:",e)

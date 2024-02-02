import pytest
import requests

def test_query_single_recipe(mock_post, fetch_single_recipe_response):
  mock_post.json.return_value = fetch_single_recipe_response
  response = requests.post( 'http://127.0.0.1:8000/graphql', data= { 
    "query": '''
              query SingleRecipe{
                singleRecipe(pk: 87){
                  message
                  recipe{
                    id
                    title
                    description
                    chef{
                      username
                      first_name
                      last_name
                    }
                    description
                    cookingTime
                    preparationTime
                    
                  }
                }
              }
              ''',
              "operationName": "SingleRecipe"
    } )
  assert response.json() == fetch_single_recipe_response
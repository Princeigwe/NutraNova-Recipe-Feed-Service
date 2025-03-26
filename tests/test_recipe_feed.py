import pytest
import requests

def test_recipe_feed(mock_post, fetch_recipe_feed_response):
  mock_post.json.return_value = fetch_recipe_feed_response
  response = requests.post( 'http://127.0.0.1:8000/graphql', data={
    "query": '''
            query RecipeFeed {
  
              recipeFeed {
                message
                suggestions
                feed {
                  recipe {
                    title
                    description
                    ingredients {
                      unit
                      quantity
                      name
                    }
                    instructions
                    preparationTime
                    cookingTime
                    images
                    tags
                    chef {
                      username
                      image
                      vote_strength
                      is_verified
                    }
                  }
                }
              }
            }

    ''',
    "operationName": "RecipeFeed"
    } )
  assert response.json() == fetch_recipe_feed_response
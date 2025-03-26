import pytest 
import requests
import json

def assert_recipe_status(fetch_single_recipe_response, fetch_draft_response):
  draft_data = json.loads(fetch_draft_response)
  published_data = json.loads(fetch_single_recipe_response)
  
  if draft_data['status'] != published_data['status']:
    pytest.fail("published recipe is not equal to draft recipe")


# this test is marked to successfully fail 
@pytest.mark.xfail()
def test_is_published(mock_post, fetch_single_recipe_response, fetch_draft_response):
  mock_post.json.return_value = fetch_draft_response
  response = requests.post( 'http://127.0.0.1:8000', data={ 
    "query": '''
              query PublishedRecipes{
                myPublishedRecipes{
                  id
                  title
                  description
                  status
                  chef{
                    username
                    first_name
                    last_name
                  }
                }
              }
              ''',
              "operationName": "PublishedRecipe"
    } )
  assert response.json() == mock_post.json.return_value
  assert_recipe_status(fetch_single_recipe_response, fetch_draft_response)
  
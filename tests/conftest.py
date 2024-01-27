import pytest
import requests

# mocking POST request of requests package
@pytest.fixture()
def mock_post(mocker):
  mock = mocker.Mock()
  mocker.patch("requests.post", return_value=mock)
  return mock


@pytest.fixture()
def recipe_response():
  response = {
    "data": {
      "createRecipe": {
        "message": "Recipe created and saved as draft",
        "recipe": {
          "id": 85,
          "title": "Sandwich",
          "description": "A very good appetizing sandwich",
          "created": "2023-12-20 15:52:31.924437+00:00",
          "ingredients": [
            {
              "name": "bread",
              "quantity": 2,
              "unit": "piece"
            },
            {
              "name": "egg",
              "quantity": 4,
              "unit": None
            },
            {
              "name": "milk",
              "quantity": 2,
              "unit": "c"
            }
          ],
          "instructions": [
            "Take your 4 eggs and fry",
            "Place the fried inbetween the two slices"
          ],
          "preparationTime": "00:05:00",
          "cookingTime": "00:00:00",
          "published": "2023-12-20 15:52:33.812623+00:00",
          "servings": 3,
          "status": "DRAFT",
          "images": [
            "https://res.cloudinary.com/nutranova/image/upload/v1700900069/boris-baldinger-VEkIsvDviSs-unsplash_KjpWHzp.jpg",
            "https://res.cloudinary.com/nutranova/image/upload/v1700900080/nicolas-j-leclercq-FyOvf63ZRpk-unsplash_CSx4GHs.jpg"
          ],
          "tags": [
            "Dinner",
            "Heart-Healthy"
          ],
          "video": None,
          "thumbnail": None,
          "nutritionalValue": {
            "calories": "697.2",
            "carbohydrates": "54.5g",
            "cholesterol": "782mg",
            "fat": "30.700000000000003g",
            "fiber": "1.6g",
            "potassium": "947mg",
            "protein": "47.400000000000006g",
            "sodium": "824mg",
            "sugar": "4.1g"
          },
          "chef": {
            "username": "bestcook",
            "first_name": "Prince",
            "last_name": "Igwe"
          }
        }
      }
    }
  }
  return response


@pytest.fixture()
def fetch_single_recipe_response():
  response = {
    "data": {
      "singleRecipe": {
        "message": "Recipe",
        "recipe": {
          "id": 87,
          "title": "Cheese Cake Heaven",
          "description": "A very good appetizing cheese cake",
          "status": "PUBLISHED",
          "chef": {
            "username": "bestcookm",
            "first_name": "Prince",
            "last_name": "Igwe"
          },
          "cookingTime": "00:00:00",
          "preparationTime": "00:05:00"
        }
      }
    }
  }
  return response


@pytest.fixture()
def fetch_draft_response():
  response = {
    "data": {
      "singleRecipe": {
        "message": "Recipe",
        "recipe": {
          "id": 87,
          "title": "Cheese Cake Heaven",
          "description": "A very good appetizing cheese cake",
          "status": "DRAFT",
          "chef": {
            "username": "bestcookm",
            "first_name": "Prince",
            "last_name": "Igwe"
          },
          "cookingTime": "00:00:00",
          "preparationTime": "00:05:00"
        }
      }
    }
  }
  return response
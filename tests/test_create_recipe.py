import pytest
import requests

def test_create_recipe(mock_post, recipe_response):
  mock_post.json.return_value = recipe_response
  response = requests.post('http://127.0.0.1:8000/graphql', data={
    "query": '''
            mutation CreateRecipe {
              createRecipe(
                input: {
                  title: "Sandwich"
                  description:"A very good appetizing sandwich"
                  ingredients: [
                    {
                      name: "bread"
                      quantity:2
                      unit: piece
                    },
                    {
                      name: "egg",
                      quantity: 4
                    },
                    {
                      name: "milk",
                      quantity: 2
                      unit: c
                    }
                  ]
                  instructions: [
                    "Take your 4 eggs and fry",
                    "Place the fried inbetween the two slices"
                  ]
                  preparation_time: {
                    minute:5
                  }
                  cooking_time: {
                    minute: 0
                  }
                  tags: ["Heart-Healthy", "Dinner"]
                  servings:3
                  images:[
                "https://res.cloudinary.com/nutranova/image/upload/v1700900069/boris-baldinger-VEkIsvDviSs-unsplash_KjpWHzp.jpg",
                "https://res.cloudinary.com/nutranova/image/upload/v1700900080/nicolas-j-leclercq-FyOvf63ZRpk-unsplash_CSx4GHs.jpg"
              ]
                thumbnail: "http://res.cloudinary.com/nutranova/video/upload/DynamoDB_NodeJS_CRUD_Example_using_NestJS_L2GS4GZ.jpg"
                video: "https://res.cloudinary.com/nutranova/video/upload/v1701360684/DynamoDB_NodeJS_CRUD_Example_using_NestJS_L2GS4GZ.mp4"
                }
                ){
                message
                recipe{
                  id
                  title
                  description
                  created
                  ingredients{
                    name
                    quantity
                    unit
                  }
                  instructions
                  preparationTime
                  cookingTime
                  published
                  servings
                  status
                  images
                  tags
                  video
                  thumbnail
                  nutritionalValue{
                    calories
                    carbohydrates
                    cholesterol
                    fat
                    fiber
                    potassium
                    protein
                    sodium
                    sugar
                  }
                  chef{
                    username
                    first_name
                    last_name
                  }
              }
            }
    ''', 
    "operationName": "CreateRecipe"
  })

  assert response.json() == recipe_response
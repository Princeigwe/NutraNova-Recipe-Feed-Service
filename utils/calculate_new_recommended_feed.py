import os
from .rabbitmq.publishers.request_recommended_feed import request_user_recommended_feed
import datetime
from utils.custom_rabbitmq_message_id import custom_rabbitmq_recipe_message_id



def calculate_new_recommended_feed(request, user):
  """this requests a new set of recommended recipes from
      the recommendations service for the current user, after 5 votes clicks for
      recipes
  """
  rabbitmq_message_type = os.environ.get('REQUEST_RECOMMENDED_FEED_MESSAGE_TYPE')
  vote_click_count = request.session.get(f"{user['username']}_vote_click_count")
  if not vote_click_count:
    request.session[f"{user['username']}_vote_click_count"] = 0
  
  vote_click_count = request.session.get(f"{user['username']}_vote_click_count")
  vote_click_count += 1 
  request.session[f"{user['username']}_vote_click_count"] = vote_click_count

  if vote_click_count == 5:
    #* send rabbitmq message to recommendation service to process recommended feed data. 

    username = user['username']
    request_user_recommended_feed({
      "message_id": custom_rabbitmq_recipe_message_id(),
      "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "type": rabbitmq_message_type, 
      "username": username
    })

    # set session like click count to zero
    request.session[f"{user['username']}_vote_click_count"] = 0

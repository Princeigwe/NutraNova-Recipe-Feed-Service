import os
from threads.kafka_request_recommended_feed_thread import RequestRecommendedFeedThread
from .rabbitmq.publishers.request_recommended_feed import request_user_recommended_feed



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
    request_user_recommended_feed({"type": rabbitmq_message_type, "username": username})

    # set session like click count to zero
    request.session[f"{user['username']}_vote_click_count"] = 0

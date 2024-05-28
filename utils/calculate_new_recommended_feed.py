from threads.kafka_request_recommended_feed_thread import RequestRecommendedFeedThread



def calculate_new_recommended_feed(request, user):
  """this requests a new set of recommended recipes from
      the recommendations service for the current user, after 5 votes clicks for
      recipes
  """

  vote_click_count = request.session.get(f"{user['username']}_vote_click_count")
  if not vote_click_count:
    request.session[f"{user['username']}_vote_click_count"] = 0
  
  vote_click_count = request.session.get(f"{user['username']}_vote_click_count")
  vote_click_count += 1 
  request.session[f"{user['username']}_vote_click_count"] = vote_click_count

  if vote_click_count == 5:
    #* send kafka message to recommendation service to process recommended feed data
    kafka_recommendation_message = user['username']
    request_recommended_feed_thread = RequestRecommendedFeedThread(kafka_recommendation_message)
    request_recommended_feed_thread.start()

    # set session like click count to zero
    request.session[f"{user['username']}_vote_click_count"] = 0

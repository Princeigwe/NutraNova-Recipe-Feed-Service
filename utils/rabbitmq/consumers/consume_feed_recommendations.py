import os
from dotenv import load_dotenv
load_dotenv()
import json
from django.core.cache import cache
from rabbitmq.rabbitmq_config import channel


def consume_user_recommended_feed(message):
  print("new message: ", message)
  message_chef_username = message.value['username']
  message_recommendations_feed = message.value['recommended_feed']

  user_recommendation_feed_cache = cache.get(f"{message_chef_username}_recommendation_feed")
  if not user_recommendation_feed_cache:
    user_recommendation_feed_cache = cache.set( key=f"{message_chef_username}_recommendation_feed", value=message_recommendations_feed, timeout=150 ) # cache timeout set to 150 seconds

  print(f"{message_chef_username}_recommendations_feed: ", cache.get(f"{message_chef_username}_recommendation_feed"))


def callback(ch, method, properties, body):
  body = json.loads(body)
  consume_user_recommended_feed(body)


# channel.basic_consume(queue, callback, auto_ack=True)
# channel.start_consuming()
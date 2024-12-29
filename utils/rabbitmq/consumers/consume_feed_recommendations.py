import os
from dotenv import load_dotenv
load_dotenv()
import json
from django.core.cache import cache
from utils.rabbitmq.channels.consume_feed_recommendations_channel import channel

rabbitmq_message_type = os.environ.get('RECOMMENDED_FEED_MESSAGE_TYPE')
exchange_name=os.environ.get('CLOUDAMQP_FANOUT_EXCHANGE')

# creating and binding queue to fanout exchange
queue = os.environ.get('CLOUDAMQP_RECOMMENDED_FEED_QUEUE')
result = channel.queue_declare(queue=queue, durable=True)
channel.queue_bind(exchange=exchange_name, queue=result.method.queue)

def consume_user_recommended_feed(message):
  if message['type'] == rabbitmq_message_type:
    print("new message: ", message)
    message_chef_username = message['username']
    message_recommendations_feed = message['recommended_feed']

    user_recommendation_feed_cache = cache.get(f"{message_chef_username}_recommendation_feed")
    if not user_recommendation_feed_cache:
      user_recommendation_feed_cache = cache.set( key=f"{message_chef_username}_recommendation_feed", value=message_recommendations_feed, timeout=150 ) # cache timeout set to 150 seconds

    print(f"{message_chef_username}_recommendations_feed: ", cache.get(f"{message_chef_username}_recommendation_feed"))


def callback(ch, method, properties, body):
  body = json.loads(body)
  consume_user_recommended_feed(body)


def consume():
  channel.basic_qos(prefetch_count=100) # setting the maximum number of in-progress mesesages to 100
  channel.basic_consume(queue, callback)
  channel.start_consuming()

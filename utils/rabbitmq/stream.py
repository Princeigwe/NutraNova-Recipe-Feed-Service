import os
from .channels.consuming_channel import channel
from .consumers.consume_chef_data import consume_and_update_chef_data
from .consumers.consume_feed_recommendations import consume_user_recommended_feed
import json

# stream declaration
stream_name=os.environ.get('RABBITMQ_STREAM')
channel.queue_declare(queue=stream_name, durable=True, arguments={"x-queue-type": "stream"})

chef_data_update_message_type = os.environ.get('CHEF_DATA_UPDATE_MESSAGE_TYPE')
recommended_feed_message_type = os.environ.get('RECOMMENDED_FEED_MESSAGE_TYPE')

def stream_message(message):
  if message['type'] == chef_data_update_message_type:
    consume_and_update_chef_data(message)
  elif message['type'] == recommended_feed_message_type:
    consume_user_recommended_feed(message)


def callback(ch, method, properties, body):
  body = json.loads(body)
  stream_message(body)


def consume():
  channel.basic_qos(prefetch_count=100) # setting the maximum number of in-progress mesesages to 100
  channel.basic_consume(stream_name, callback, arguments={"x-stream-offset": "first"})
  channel.start_consuming()
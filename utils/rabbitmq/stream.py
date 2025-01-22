import os
from .channels.consuming_channel import channel
from .consumers.consume_chef_data import consume_and_update_chef_data
from .consumers.consume_feed_recommendations import consume_user_recommended_feed
import json

# stream declaration
stream_name=os.environ.get('RABBITMQ_STREAM')

chef_data_update_message_type = os.environ.get('CHEF_DATA_UPDATE_MESSAGE_TYPE')
recommended_feed_message_type = os.environ.get('RECOMMENDED_FEED_MESSAGE_TYPE')

def stream_message(message):
  if message['type'] == chef_data_update_message_type:
    consume_and_update_chef_data(message)
  elif message['type'] == recommended_feed_message_type:
    consume_user_recommended_feed(message)


# def callback(ch, method, properties, body):
#   body = json.loads(body)
#   stream_message(body)


def callback(channel, method_frame, header_frame, body):

  # Getting the delivery tag of the current message
  latest_delivery_tag = method_frame.delivery_tag
  body = json.loads(body)
  stream_message(body)
  channel.basic_ack(latest_delivery_tag)

def consume():

    # setting the limit for "in-progress" messages
    channel.basic_qos(prefetch_count=100)
    channel.basic_consume(stream_name, callback, arguments={"x-stream-offset": "first"})
    channel.start_consuming()

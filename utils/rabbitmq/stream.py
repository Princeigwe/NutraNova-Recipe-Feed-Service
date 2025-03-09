import os
from .channels.consuming_channel import channel
from .consumers.consume_chef_data import consume_and_update_chef_data
from .consumers.consume_feed_recommendations import consume_user_recommended_feed
from django.conf import settings
from utils.cursor_rabbitmq_postgres_operations import update_custom_rabbitmq_user_message_ids
import json

# stream declaration
stream_name=os.environ.get('RABBITMQ_STREAM')

channel.queue_declare(queue=stream_name, durable=True, arguments={
  "x-queue-type": "stream", 
  "x-max-age": "1D",
  "x-max-length-bytes": 5000000, 
  "x-stream-max-segment-size-bytes":5000
  }) 

chef_data_update_message_type = os.environ.get('CHEF_DATA_UPDATE_MESSAGE_TYPE')
recommended_feed_message_type = os.environ.get('RECOMMENDED_FEED_MESSAGE_TYPE')

def stream_message(message):
  """
  The `stream_message` function processes different types of messages based on their type and updates
  chef data or consumes user recommended feed accordingly.
  
  :param message: The `stream_message` function takes a `message` parameter, which is expected to be a
  dictionary containing information about a message. The function checks the `type` key in the message
  dictionary to determine the type of message it is processing
  """
  if message['type'] == chef_data_update_message_type:
    consumed_rabbitmq_message_ids = settings.RABBITMQ_USER_MESSAGE_IDS
    if message['message_id'] not in consumed_rabbitmq_message_ids:
      print("Consuming user data rabbitmq message...")
      consume_and_update_chef_data(message)
      update_custom_rabbitmq_user_message_ids(message['message_id'], message['created_at']) # insert the consumed message id in the custom rabbitmq user message id table
    else:
      print("Message already consumed")
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

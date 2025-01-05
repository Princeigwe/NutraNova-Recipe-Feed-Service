import os
from .channels.consuming_channel import channel
from .consumers.consume_chef_data import consume_and_update_chef_data
from .consumers.consume_feed_recommendations import consume_user_recommended_feed
import json
from utils.rabbitmq_offset_track import update_offset_record, get_offset_record
from django.conf import settings


# stream declaration
stream_name=os.environ.get('RABBITMQ_STREAM')
queue = channel.queue_declare(queue=stream_name, durable=True, arguments={"x-queue-type": "stream"})
queue_length = queue.method.message_count

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
  number_of_ackd_message = 0

  # Getting the delivery tag of the current message
  latest_delivery_tag = method_frame.delivery_tag

  body = json.loads(body)
  stream_message(body)

  channel.basic_ack(latest_delivery_tag)

  number_of_ackd_message = number_of_ackd_message + 1
  
  offset_record = get_offset_record(1)
  offset_value = offset_record[1]
  new_offset_value = offset_value + number_of_ackd_message
  update_offset_record(1, new_offset_value)

def consume():

    # setting the limit for "in-progress" messages
    channel.basic_qos(prefetch_count=100)
    
    channel.basic_consume(
        stream_name, 
        callback, 
        arguments={"x-stream-offset": settings.RABBITMQ_OFFSET_VALUE}
    )

    channel.start_consuming()

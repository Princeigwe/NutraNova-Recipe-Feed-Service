import logging
import json
from pika.exceptions import AMQPError
from utils.rabbitmq.channels.publish_request_recommended_feed_channel import channel
import os

exchange_name=os.environ.get('CLOUDAMQP_FANOUT_EXCHANGE')

def request_user_recommended_feed(message: dict):
  try:
    channel.basic_publish(exchange=exchange_name, routing_key='', body=json.dumps(message)) # publishing to fanout exchange
    print ("[RabbitMQ]: Message sent for requesting recommendation feed for user")
  except AMQPError as e:
    logging.exception(e)

# def request_user_recommended_feed(username_message):
#   future = kafka_config.producer.send(topic, username_message)
  
#   try:
#     metadata = future.get()
#     print(metadata)
#     print(f" {username_message}'s recommendations message sent")
#   except KafkaError as e:
#    logging.exception(e)
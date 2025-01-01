import logging
import json
from pika.exceptions import AMQPError
# from utils.rabbitmq.channels.publish_published_recipe_channel import channel
from utils.rabbitmq.channels.publishing_channel import channel, connection
import os

# exchange_name=os.environ.get('CLOUDAMQP_FANOUT_EXCHANGE')
stream_name=os.environ.get('RABBITMQ_STREAM')

def send_graph_nodes_details(message: dict):
  try:
    channel.basic_publish(exchange='', routing_key=stream_name, body=json.dumps(message))
    print ("[RabbitMQ]: Message sent to stream")
  except AMQPError as e:
    logging.exception(e)

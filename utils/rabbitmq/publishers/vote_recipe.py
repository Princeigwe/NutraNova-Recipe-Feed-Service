import logging
import json
from pika.exceptions import AMQPError
from utils.rabbitmq.channels.publishing_channel import channel
import os

stream_name=os.environ.get('RABBITMQ_STREAM')



def send_chef_vote_recipe_details(message:dict):
  try:
    channel.basic_publish(exchange='', routing_key=stream_name, body=json.dumps(message))
    print ("[RabbitMQ]: Message sent to stream for recipe vote")
  except AMQPError as e:
    logging.exception(e)
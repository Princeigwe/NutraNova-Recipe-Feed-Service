import logging
import json
from pika.exceptions import AMQPError
from utils.rabbitmq.channels.publish_published_recipe_channel import channel
import os

exchange_name=os.environ.get('CLOUDAMQP_FANOUT_EXCHANGE')
def send_graph_nodes_details(message: dict):
  try:
    channel.basic_publish(exchange=exchange_name, routing_key='', body=json.dumps(message)) # publishing to fanout exchange
    print ("cloudamqp: Message sent to consumer")
  except AMQPError as e:
    logging.exception(e)

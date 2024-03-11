from kafka.errors import KafkaError
import logging
import os
from dotenv import load_dotenv
load_dotenv()
from utils.kafka import kafka_config

topic = os.environ.get('UPSTASH_KAFKA_CHEF_UNLIKE_REL_RECIPE_TOPIC')
if type(topic) == bytes:
  topic = topic.decode('utf-8')


def send_delete_chef_like_recipe_details(message: dict):
  future = kafka_config.producer.send(topic, message)

  try:
    metadata = future.get()
    print(metadata)
    print("message sent")
  except KafkaError as e:
    logging.exception(e)
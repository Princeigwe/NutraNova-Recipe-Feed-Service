from kafka.errors import KafkaError
import logging
import os
from dotenv import load_dotenv
load_dotenv()
from utils.kafka import kafka_config

topic = os.environ.get('UPSTASH_KAFKA_REQUEST_USER_RECOMMENDATIONS_TOPIC')
if type(topic) == bytes:
  topic = topic.decode('utf-8')


def request_user_recommended_feed(username_message):
  future = kafka_config.producer.send(topic, username_message)
  
  try:
    metadata = future.get()
    print(metadata)
    print(f" {username_message}'s recommendations message sent")
  except KafkaError as e:
    logging.exception(e)
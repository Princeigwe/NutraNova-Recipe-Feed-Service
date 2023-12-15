from kafka import KafkaConsumer
import os
from dotenv import load_dotenv
load_dotenv()
import json


def consume_and_update_chef_username():
  print("Kafka consumer to be initialized")
  topic = os.environ.get('USERNAME_CHEF_TOPIC')
  consumer = KafkaConsumer(topic, bootstrap_servers=[os.environ.get('NUTRANOVA_KAFKA_SERVER')], auto_offset_reset='earliest', value_deserializer=lambda m: json.loads(m.decode('ascii')), api_version=(0, 10, 2))
  for message in consumer:
    print(message.value)
    return{
      "topic": message.topic,
      "message": message.value
    }
  

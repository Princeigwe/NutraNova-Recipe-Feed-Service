from kafka import KafkaConsumer
import os
from dotenv import load_dotenv
load_dotenv()
import json


def consume_and_update_chef_username():
  print("Kafka consumer to be initialized")

  consumer_config = {
    'bootstrap_servers': os.environ.get('UPSTASH_KAFKA_ENDPOINT'),
    'sasl_mechanism': 'SCRAM-SHA-256',
    'security_protocol': 'SASL_SSL',
    'sasl_plain_username': os.environ.get('UPSTASH_KAFKA_USERNAME'),
    'sasl_plain_password': os.environ.get('UPSTASH_KAFKA_PASSWORD'),
    'auto.offset.reset': 'latest'
  }
  topic = os.environ.get('UPSTASH_KAFKA_CHEF_USERNAME_TOPIC')

  # adding "api_version" on initialization fixes the issue "kafka.errors.NoBrokersAvailable"
  consumer = KafkaConsumer(
    topic,
    bootstrap_servers=consumer_config['bootstrap_servers'],
    sasl_mechanism=consumer_config['sasl_mechanism'],
    security_protocol=consumer_config['security_protocol'],
    sasl_plain_username=consumer_config['sasl_plain_username'],
    sasl_plain_password=consumer_config['sasl_plain_password'],
    auto_offset_reset=consumer_config['auto.offset.reset'],
    value_deserializer=lambda m: json.loads(m.decode('ascii')),
    api_version=(0, 10, 2)
)

  # for message in consumer:
  #   print(message.value)
  #   return{
  #     "topic": message.topic,
  #     "message": message.value
  #   }

  try:
    for message in consumer:
      print(f"Received message: {message.value}")
  except KeyboardInterrupt:
    pass
  finally:
    consumer.close()
  

# consume_and_update_chef_username()
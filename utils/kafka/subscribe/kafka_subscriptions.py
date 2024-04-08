from kafka import KafkaConsumer
import os
from dotenv import load_dotenv
load_dotenv()
import json
from django.core.cache import cache


def consume_kafka_messages():
  consumer_config = {
    'bootstrap_servers': os.environ.get('UPSTASH_KAFKA_ENDPOINT'),
    'sasl_mechanism': 'SCRAM-SHA-256',
    'security_protocol': 'SASL_SSL',
    'sasl_plain_username': os.environ.get('UPSTASH_KAFKA_USERNAME'),
    'sasl_plain_password': os.environ.get('UPSTASH_KAFKA_PASSWORD'),
    'auto.offset.reset': 'latest'
  }

  UPSTASH_KAFKA_CHEF_USERNAME_TOPIC = os.environ.get('UPSTASH_KAFKA_CHEF_USERNAME_TOPIC')
  UPSTASH_KAFKA_SEND_USER_RECOMMENDATIONS_TOPIC = os.environ.get('UPSTASH_KAFKA_SEND_USER_RECOMMENDATIONS_TOPIC')

  topics = [ UPSTASH_KAFKA_CHEF_USERNAME_TOPIC, UPSTASH_KAFKA_SEND_USER_RECOMMENDATIONS_TOPIC ]

  # adding "api_version" on initialization fixes the issue "kafka.errors.NoBrokersAvailable"
  consumer = KafkaConsumer(
    # topic,
    bootstrap_servers=consumer_config['bootstrap_servers'],
    sasl_mechanism=consumer_config['sasl_mechanism'],
    security_protocol=consumer_config['security_protocol'],
    sasl_plain_username=consumer_config['sasl_plain_username'],
    sasl_plain_password=consumer_config['sasl_plain_password'],
    auto_offset_reset=consumer_config['auto.offset.reset'],
    value_deserializer=lambda m: json.loads(m.decode('ascii')),
    api_version=(0, 10, 2)
  )

  consumer.subscribe(topics)
  while True:
    # fetch and return records in batches by topic-partition by polling
    all_records = consumer.poll(timeout_ms=100, max_records=100)

    # for each topic, retrieve all messages in the record
    # call the functions for their respective messages
    for topic_partition, messages in all_records.items():
      if topic_partition.topic == UPSTASH_KAFKA_CHEF_USERNAME_TOPIC:
        consume_and_update_chef_username(messages)
      elif topic_partition.topic == UPSTASH_KAFKA_SEND_USER_RECOMMENDATIONS_TOPIC:
        consume_user_recommended_feed(messages)


def consume_and_update_chef_username(messages):
  for message in messages:
    try:
      print(f"Received message: {message.value}")
      # import statement for model is placed here because of the "Apps aren't loaded yet" message on Django server startup with background 
      from recipes.models import Chef
      chef = Chef.objects.get(username=message.value['old_username'])
      chef.username = message.value['new_username']
      chef.save()
      print(f"{chef.first_name} username is now {chef.username}")
    except Chef.DoesNotExist:
      pass
    except KeyboardInterrupt:
      pass


def consume_user_recommended_feed(messages):
  for message in messages:
    print("new message: ", message)
    message_chef_username = message.value['username']
    message_recommendations_feed = message.value['recommended_feed']

    user_recommendation_feed_cache = cache.get(f"{message_chef_username}_recommendation_feed")
    if not user_recommendation_feed_cache:
      user_recommendation_feed_cache = cache.set( key=f"{message_chef_username}_recommendation_feed", value=message_recommendations_feed, timeout=300 ) # cache timeout set to 100 seconds

  print(f"{message_chef_username}_recommendations_feed: ", cache.get(f"{message_chef_username}_recommendation_feed"))




# def consume_and_update_chef_username():
#   print("Kafka consumer to be initialized")

#   consumer_config = {
#     'bootstrap_servers': os.environ.get('UPSTASH_KAFKA_ENDPOINT'),
#     'sasl_mechanism': 'SCRAM-SHA-256',
#     'security_protocol': 'SASL_SSL',
#     'sasl_plain_username': os.environ.get('UPSTASH_KAFKA_USERNAME'),
#     'sasl_plain_password': os.environ.get('UPSTASH_KAFKA_PASSWORD'),
#     'auto.offset.reset': 'latest'
#   }
#   topic = os.environ.get('UPSTASH_KAFKA_CHEF_USERNAME_TOPIC')

#   # adding "api_version" on initialization fixes the issue "kafka.errors.NoBrokersAvailable"
#   consumer = KafkaConsumer(
#     topic,
#     bootstrap_servers=consumer_config['bootstrap_servers'],
#     sasl_mechanism=consumer_config['sasl_mechanism'],
#     security_protocol=consumer_config['security_protocol'],
#     sasl_plain_username=consumer_config['sasl_plain_username'],
#     sasl_plain_password=consumer_config['sasl_plain_password'],
#     auto_offset_reset=consumer_config['auto.offset.reset'],
#     value_deserializer=lambda m: json.loads(m.decode('ascii')),
#     api_version=(0, 10, 2)
# )


#   try:
#     for message in consumer:
#       print(f"Received message: {message.value}")
#       # import statement for model is placed here because of the "Apps aren't loaded yet" message on Django server startup with background 
#       from recipes.models import Chef
#       chef = Chef.objects.get(username=message.value['old_username'])
#       chef.username = message.value['new_username']
#       chef.save()
#       print(f"{chef.first_name} username is now {chef.username}")
#   except KeyboardInterrupt:
#     pass
#   finally:
#     consumer.close()
  

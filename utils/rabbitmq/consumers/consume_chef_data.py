import os
from dotenv import load_dotenv
load_dotenv()
import json
from django.core.cache import cache
# from utils.rabbitmq.rabbitmq_config import channel
from utils.rabbitmq.channels.consume_chef_data_channel import channel
import os

rabbitmq_message_type = os.environ.get('CHEF_DATA_UPDATE_MESSAGE_TYPE')


exchange_name=os.environ.get('CLOUDAMQP_FANOUT_EXCHANGE')

# creating and binding queue to fanout exchange
queue = os.environ.get('CLOUDAMQP_RECIPE_CHEF_DATA_UPDATE_QUEUE')
result = channel.queue_declare(queue=queue, durable=True)
channel.queue_bind(exchange=exchange_name, queue=result.method.queue)

def consume_and_update_chef_data(message):
  if message['type'] == rabbitmq_message_type:
    try:
      print(f"Received message: {message}")

      from recipes.models import Chef

      if 'old_username' in message:
        chef = Chef.objects.get(username=message['old_username'])
        chef.username = message['new_username']
        chef.save()
        print(f"{chef.username} username updated")
      
      # this is a response operation for the 'updateProfile' resolver in the user microservice
      else:
        chef = Chef.objects.get(username=message['username'])
        chef.image = message['image'] if 'image' in message else chef.image
        chef.first_name = message['first_name'] if 'first_name' in message else chef.first_name
        chef.last_name = message['last_name'] if 'last_name' in message else chef.last_name
        chef.vote_strength = message['vote_strength'] if 'vote_strength' in message else chef.vote_strength
        chef.is_verified = message['is_verified'] if 'is_verified' in message else chef.vote_strength
        chef.save()
        print(f"{chef.username} data updated")
    
    except Chef.DoesNotExist:
      pass
    except KeyboardInterrupt:
      pass


def callback(ch, method, properties, body):
  body = json.loads(body)
  consume_and_update_chef_data(body)


def consume():
  channel.basic_consume(queue, callback)
  channel.start_consuming()




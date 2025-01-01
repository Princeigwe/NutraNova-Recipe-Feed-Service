import os
from dotenv import load_dotenv
load_dotenv()
import os


stream_name = os.environ.get('RABBITMQ_STREAM')
def consume_and_update_chef_data(message):
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


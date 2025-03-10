import uuid
import random
import string

def generate_unique_alphanumeric_id():
  unique_id = str(uuid.uuid4())
  random_alphanumeric = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
  custom_id = unique_id + random_alphanumeric
  return custom_id


def custom_rabbitmq_recipe_message_id():
  recipe_message_id = "NNR::" + generate_unique_alphanumeric_id()
  return recipe_message_id
from threading import Thread
from utils.kafka.produce.delete_neo_graph_chef_like_recipe_rel import send_delete_chef_like_recipe_details

class GraphChefUnLikeRecipeThread(Thread):
  def __init__(self, kafka_message: dict):
      Thread.__init__(self)
      self.kafka_message = kafka_message

  def run(self):
    send_delete_chef_like_recipe_details(self.kafka_message)
    print("kafka message sent in background")
  
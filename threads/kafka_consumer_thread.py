from threading import Thread
from utils.kafka.subscribe.kafka_subscriptions import consume_and_update_chef_username, consume_kafka_messages

class UpdateChefThread(Thread):
  """this thread will be responsible for running the kafka consumer that will be listening for updated usernames to update chef data, in the background"""
  def __init__(self):
    Thread.__init__(self)

  def run(self):
    print("Thread running in background")
    consume_kafka_messages()
from threading import Thread
from utils.rabbitmq.consumers.consume_chef_data import consume


class UpdateChefThread(Thread):
  """this thread will be responsible for running the kafka consumer that will be listening for updated usernames to update chef data, in the background"""
  def __init__(self):
    Thread.__init__(self)

  def run(self):
    print("[RabbitMQ]: 'update chef data' consumer thread running in background")
    consume()
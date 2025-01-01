from threading import Thread
from utils.rabbitmq.stream import consume

class StreamMessageThread(Thread):
  """this thread will be responsible for running the kafka consumer that will be listening for updated usernames to update chef data, in the background"""
  def __init__(self):
    Thread.__init__(self)

  def run(self):
    print("[RabbitMQ]: 'rabbitmq stream' thread running in background")
    consume()
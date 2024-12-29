from threading import Thread
from utils.rabbitmq.consumers.consume_feed_recommendations import consume


class ConsumeRecommendedFeedThread(Thread):
  """this thread will be responsible for running the kafka consumer that will be listening for recommended feed, in the background"""
  def __init__(self):
    Thread.__init__(self)

  def run(self):
    print("[RabbitMQ]: 'consume-recommended-feed' consumer thread running in background")
    consume()
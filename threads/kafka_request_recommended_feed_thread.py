from threading import Thread
from utils.kafka.produce.request_recommended_feed import request_user_recommended_feed


class RequestRecommendedFeedThread(Thread):
  def __init__(self, kafka_message: str):
      Thread.__init__(self)
      self.kafka_message = kafka_message
  

  def run(self):
    request_user_recommended_feed(self.kafka_message)
    print("kafka recommendation message sent in background")
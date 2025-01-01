## this file is a custom command created from running rabbitmq consumer in the background, in order to update chef details. "python3 manage.py rabbitmq_consumers"

from typing import Any
from django.core.management.base import BaseCommand
from threads import rabbitmq_stream_thread


class Command(BaseCommand):
  help = "Starting RabbitMQ consumers"

  def handle(self, *args: Any, **options: Any) -> str | None:
    # # start rabbitmq consumer thread for updating chef data
    # update_chef_data_consumer = rabbitmq_consumer_update_chef_thread.UpdateChefThread()
    # update_chef_data_consumer.start()

    # # start rabbitmq consumer thread for consuming recommended feed from the recommendations service
    # consume_recommended_feed_consumer = rabbitmq_consumer_recommended_feed_thread.ConsumeRecommendedFeedThread()
    # consume_recommended_feed_consumer.start()

    rabbitmq_stream = rabbitmq_stream_thread.StreamMessageThread()
    rabbitmq_stream.start()


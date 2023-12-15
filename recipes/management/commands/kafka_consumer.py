## this file is a custom command created from running kafka consumer in the background, in order to update chef details. "python3 manage.py kafka_consumer"

from typing import Any
from django.core.management.base import BaseCommand
from threads import kafka_consumer_thread

class Command(BaseCommand):
  help = "Start Kafka consumer"

  def handle(self, *args: Any, **options: Any) -> str | None:
    kafka_consumer = kafka_consumer_thread.UpdateChefThread()
    kafka_consumer.start()
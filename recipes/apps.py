from django.apps import AppConfig
# from utils.kafka.subscribe.kafka_subscriptions import consume_and_update_chef_username
import os
from django.core.management import call_command


class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    function_executed = False

    def ready(self) -> None:
        if os.environ.get('RUN_MAIN'):
            print("hello server")
            call_command('kafka_consumer') # calling the custom "kafka_consumer" command
            self.function_executed = True

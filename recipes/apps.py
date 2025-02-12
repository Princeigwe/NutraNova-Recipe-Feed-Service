from django.apps import AppConfig
import os
from django.core.management import call_command

class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    function_executed = False

    def ready(self) -> None:
        if os.environ.get('RUN_MAIN'):
            print("hello server")
            call_command('execute_schedules') # calling the custom "execute_schedules" command
            call_command('rabbitmq_consumers')
            self.function_executed = True

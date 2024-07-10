from django.apps import AppConfig
import os
from .mongo_database import client


class StoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stories'
    function_executed = False

    def ready(self) -> None:
        if os.environ.get('RUN_MAIN'):
            try:
                client.admin.command('ping')
                print(" ")
                print("Pinged your deployment. You successfully connected to MongoDB!")
            except Exception as e:
                print(e)
            self.function_executed = True
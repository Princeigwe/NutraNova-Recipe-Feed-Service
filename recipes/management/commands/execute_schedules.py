## this file is a custom command created for executing scheduled jobs in the background,
#  in order to auto-request users recommended feed from recommendations microservice. "python3 manage.py execute_schedules"

from typing import Any
from django.core.management import BaseCommand
from threads import execute_schedules_thread

class Command(BaseCommand):
  help = "Start Python Scheduler"

  def handle(self, *args: Any, **options: Any) -> str | None: 
    scheduler = execute_schedules_thread.ExecuteSchedulesThread()
    scheduler.start()
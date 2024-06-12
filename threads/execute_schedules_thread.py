from threading import Thread
from utils.schedules import execute_schedules

class ExecuteSchedulesThread(Thread):
  """this thread will be responsible for executing all scheduled jobs in the background"""
  def __init__(self):
    Thread.__init__(self)
  
  def run(self):
    print("Scheduler thread running in background")
    execute_schedules()
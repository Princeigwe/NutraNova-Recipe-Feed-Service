import datetime as dt
from scheduler import Scheduler
import time
from .auto_recommended_feed_request import auto_request_recommended_feeds

# *: scheduled jobs must be in the same file with the function executing them

# scheduling jobs
schedule = Scheduler()
schedule.cyclic(dt.timedelta(seconds=120), auto_request_recommended_feeds)


# executing all scheduled jobs
def execute_schedules():
    while True:
        schedule.exec_jobs()
        time.sleep(1)

import datetime as dt
from scheduler import Scheduler
import time
from .auto_recommended_feed_request import auto_request_recommended_feeds
from .expired_stories import delete_expired_stories

# *: scheduled jobs must be in the same file with the function executing them

# scheduling jobs
schedule = Scheduler()
schedule.cyclic(dt.timedelta(seconds=120), auto_request_recommended_feeds) # run after every 120 seconds
schedule.minutely(dt.time(second=15), delete_expired_stories) # run at the 15th second of every minute


# executing all scheduled jobs
def execute_schedules():
    while True:
        schedule.exec_jobs()
        time.sleep(1)

from stories.mongo_database import database
from datetime import datetime, timedelta
import calendar

stories = database.recipe_stories

def fetch_expired_stories():
  """stories have 24 hours period"""
  
  expired_stories = []

  current_time = datetime.now()
  current_epoch_time = calendar.timegm(current_time.timetuple())
  print("current epoch time: ", current_epoch_time)

  all_stories = stories.find()
  for story in all_stories:
    story_date = story.date
    story_expiry_date = story_date + timedelta(days=1)
    story_expiry_epoch_time = calendar.timegm(story_expiry_date.timetuple())
    print(story_expiry_epoch_time)

    if story_expiry_epoch_time >= current_epoch_time:
      expired_stories.append(story)
  
  return expired_stories


def delete_expired_stories():
  print("Deleting expired stories")
  fetched_expired_stories = fetch_expired_stories()

  print("fetched expired stories: ", fetch_expired_stories)
  for story in fetched_expired_stories:
    stories.delete_one({"_id": story._id})

  print("Expired stories deleted")
  print("fetched expired stories: ", fetch_expired_stories)
  
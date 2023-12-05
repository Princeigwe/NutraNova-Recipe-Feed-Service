from threading import Thread
from utils.upload_video import upload_video_and_thumbnail

# The `UploadVideoThread` class is a subclass of `Thread` that uploads a video file with the upload_video_and_thumbnail function
# in a separate thread.
class UploadVideoThread(Thread):
  def __init__(self, file):
    Thread.__init__(self)
    self.file = file
    self.video = None
    self.thumbnail = None
  
  def run(self) -> None:
    upload = upload_video_and_thumbnail(self.file)
    print(upload)
    self.video = upload['video']
    self.thumbnail = upload['thumbnail']

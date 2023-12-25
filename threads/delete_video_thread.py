from threading import Thread
from utils.delete_video import delete_cloudinary_video_asset

class DeleteVideoThread(Thread):
  def __init__(self, public_id):
    Thread.__init__(self)
    self.public_id = public_id

  def run(self):
    delete_cloudinary_video_asset(self.public_id)
    print(f"old video asset; {self.public_id} deleted")
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()


def compress_image(image):
  image_path = os.path.join(os.getcwd().image)
  image = Image.open(image_path)
  compressed_image = image.save(f"compressed_{image}", optimize=True, quality=20)
  print(compressed_image)
  return compressed_image
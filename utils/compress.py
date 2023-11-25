from PIL import Image
import os
from dotenv import load_dotenv
from django.conf import settings

load_dotenv()


def compress_image(image):
  # access the image file
  image_path = os.path.join(os.getcwd(), image)
  print(image)
  print(image_path)
  image = Image.open(image_path)
  width, height = image.size

  new_size = (width//2, height//2)
  resized_image = image.resize(new_size)
  
  # replacing the original image with the compressed image
  resized_image.save(image_path, 'JPEG', optimize=True, quality=90)
  # return image_path # the new compressed image
  return 1
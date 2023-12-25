import os
import jwt


secret_key = os.environ.get('JWT_SECRET_KEY')

def decode_access_token(token):
  try:
    decoded_data = jwt.decode(jwt=token, key=secret_key, algorithms=["HS256"])
    return decoded_data
  except jwt.ExpiredSignatureError as e:
    message = f'Invalid token: {e}'
    raise Exception(message)
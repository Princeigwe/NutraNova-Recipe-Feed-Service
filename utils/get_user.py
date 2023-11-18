from .jwt_decode import decode_access_token


def get_user(info):
  """this function is meant to fetch the details of the user, created by the users' service, from the jwt in Authorization header"""
  request = info.context["request"] # get http request from info.context
  authorization_header = request.headers.get("Authorization") # retrieve Authorization header to fetch value
  if not authorization_header:
    raise Exception("Authorization header not found")
  parts = authorization_header.split(" ") # split value by the space
  token = parts[1] # get the token
  decoded_data = decode_access_token(token) # decode token

  # decoded token payload keys to remove
  unwanted_keys = ["iss", "iat", "exp"]
  for key in unwanted_keys:
    decoded_data.pop(key, None)
  
  # modified decoded_data is now the user details
  user = decoded_data
  return user
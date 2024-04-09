from rest_framework.response import Response
from rest_framework import status
from utils.jwt_decode import decode_access_token
from functools import wraps

def jwt_authorization(func):
  @wraps(func) # this fixes the issue of rendering process when used with DRF api_view decorator
  def wrapper(request): # working with the "request" parameter of the function the decorator will act on

    try:
      authorization_header = request.headers.get("Authorization") 
      if not authorization_header:
        return Response({"message": "Unauthorized request"}, status=status.HTTP_400_BAD_REQUEST)
      parts = authorization_header.split(" ")
      token = parts[1] 
      decode_access_token(token) 
      return func(request) # wrapped function with its parameter

    # if there is an exception from the decode_access_token is raised, return jwt expired error message
    except Exception as error:
      print(error)
      return Response(
        {"message": "invalid jwt"},
        status=status.HTTP_401_UNAUTHORIZED
      )
    
  return wrapper
from rest_framework.response import Response
from rest_framework import status
from utils.jwt_decode import decode_access_token

def is_authenticated(func):
  def wrapper(request):

    authorization_header = request.headers.get("Authorization") 
    if not authorization_header:
      return Response({"message": "Unauthorized request"}, status=status.HTTP_400_BAD_REQUEST)
    parts = authorization_header.split(" ")
    token = parts[1] 
    decode_access_token(token) 

    func(request)
  return wrapper
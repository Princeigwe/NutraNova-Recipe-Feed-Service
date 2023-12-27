import requests
import os
from dotenv import load_dotenv
load_dotenv()
import json

def fetch_user_followings(user_username, access_token):
  try:
    user_service_api_endpoint = os.environ.get('USER_SERVICE_API_ENDPOINT')
    headers = { "Authorization": f"Bearer {access_token}", 'Content-Type': 'application/json' }
    query = f"""
            query UserFollowing {{
                userFollowing(username: "{user_username}") {{
                    number
                    users {{
                        username
                    }}
                }}
            }}
            """
    response = requests.post( 
      user_service_api_endpoint, 
      headers=headers,
      data= json.dumps( {
        "query": query,
        "operationName": "UserFollowing"
      } )
    )
    return response.json()
  except requests.exceptions.ConnectionError as e:
    print ("Error Connecting:",e)
  except requests.exceptions.Timeout as e:
    print ("Timeout Error:",e)
  except requests.exceptions.RequestException as e:
    print ("Something went wrong:",e)


# fetch_user_followings("igwep297", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImJlc3Rjb29rbSIsImVtYWlsIjoicGY3MDg0OTVAZ21haWwuY29tIiwiZmlyc3RfbmFtZSI6IlByaW5jZSIsImxhc3RfbmFtZSI6IkZhdm91ciIsImFnZSI6IjI5IiwiZ2VuZGVyIjoiTUFMRSIsInJvbGUiOiJVU0VSIiwiZGlldGFyeV9wcmVmZXJlbmNlIjoiREFJUllfRlJFRSIsInRhc3RlX3ByZWZlcmVuY2VzIjpbIkFST01BVElDIiwiU09VUiJdLCJoZWFsdGhfZ29hbCI6IldFSUdIVF9MT1NTIiwiYWxsZXJnZW5zIjpbIk1JTEsiXSwiYWN0aXZpdHlfbGV2ZWwiOiJMSUdIVExZX0FDVElWRSIsImN1aXNpbmVzIjpbIklORElBTiIsIkFTSUFOIl0sIm1lZGljYWxfY29uZGl0aW9ucyI6WyJQUkVHTkFOQ1kiXSwiaXNfb25fYm9hcmRlZCI6dHJ1ZSwiaXNzIjoiaHR0cDovLzEyNy4wLjAuMTo4MDAwLyIsImlhdCI6MTcwMzQ1MjI3MywiZXhwIjoxNzAzNTM4NjczfQ._T-PnCKmKWb05CvsRO7dNwo6RG6tzwLHjloZFpwg6rU")

import redis
import os
from .rabbitmq.publishers.request_recommended_feed import request_user_recommended_feed


def fetch_redis_keys():
    redis_keys = []

    redis_url = os.environ.get('REDIS_URL')
    r = redis.from_url(
        url=redis_url,
        health_check_interval=10,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        socket_keepalive=True
    )

    for key in r.keys():
        key = key.decode('utf-8')
        redis_keys.append(key)
    return redis_keys


def getUserNameFromCacheKey(input_string):
    """this function extracts the "<username>" from ':1:<username>_followings'"""
    first_colon_index = input_string.find(':')
    second_colon_index = input_string.find(':', first_colon_index + 1)
    third_colon_index = input_string.find('_', second_colon_index + 1)

    substring = input_string[second_colon_index + 1:third_colon_index]
    return substring


def auto_request_recommended_feeds():
    rabbitmq_message_type = os.environ.get('REQUEST_RECOMMENDED_FEED_MESSAGE_TYPE')
    """ this function will be used together with Python Scheduler()
        to automatically request for recipe feeds recommended by the recommendation microservice,
        for every on-boarded user that has a following
    """

    redis_keys = fetch_redis_keys()
    print("NutraNova Recipe Redis Keys: ", redis_keys)

    users_with_followings = []
    for item in redis_keys:
        if "followings" in item:
            users_with_followings.append(item)

    usernames = []
    # extracting "<username>" from ':1:<username>_followings'
    for item in users_with_followings:
        extracted_username = getUserNameFromCacheKey(item)
        usernames.append(extracted_username)
    print("caches of usernames with followings: ", usernames)

    for username in usernames:
        # request_user_recommended_feed(username)
        request_user_recommended_feed({"type": rabbitmq_message_type, "username": username})
        print(f"Auto-feed request for {username} with message type: {rabbitmq_message_type}")




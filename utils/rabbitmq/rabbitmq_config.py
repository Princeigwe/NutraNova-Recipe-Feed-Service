import pika, os, logging
from pika.exceptions import AMQPError
import json

url = os.environ.get('CLOUDAMQP_URL')
params = pika.URLParameters(url)
params.heartbeat = 0

connection = pika.BlockingConnection(params)
channel = connection.channel()
import pika, os

ENVIRONMENT = os.environ.get("ENVIRONMENT", default="production" )

url = os.environ.get('CLOUDAMQP_URL') if ENVIRONMENT == 'production' else "amqp://guest:guest@rabbitmq:5672/"

params = pika.URLParameters(url)
params.heartbeat = 0

connection = pika.BlockingConnection(params)
channel = connection.channel()
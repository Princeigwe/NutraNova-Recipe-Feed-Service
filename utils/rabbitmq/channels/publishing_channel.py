import pika, os

url = os.environ.get('CLOUDAMQP_URL')
params = pika.URLParameters(url)
params.heartbeat = 0

connection = pika.BlockingConnection(params)
channel = connection.channel()

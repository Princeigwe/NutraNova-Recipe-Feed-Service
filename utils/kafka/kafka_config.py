from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging
import os
from dotenv import load_dotenv
load_dotenv()
import json

producer_config = {
        'bootstrap_servers': os.environ.get('UPSTASH_KAFKA_ENDPOINT'),
        'sasl_mechanism': 'SCRAM-SHA-256',
        'security_protocol': 'SASL_SSL',
        'sasl_plain_username': os.environ.get('UPSTASH_KAFKA_USERNAME'),
        'sasl_plain_password': os.environ.get('UPSTASH_KAFKA_PASSWORD'),
    }

# adding "api_version" on initialization fixes the issue "kafka.errors.NoBrokersAvailable"
producer = KafkaProducer(bootstrap_servers=producer_config['bootstrap_servers'],
                        sasl_mechanism=producer_config['sasl_mechanism'],
                        security_protocol=producer_config['security_protocol'],
                        sasl_plain_username=producer_config['sasl_plain_username'],
                        sasl_plain_password=producer_config['sasl_plain_password'],
                        value_serializer=lambda m: json.dumps(m).encode('ascii'),
                        api_version=(2, 0, 0)
)

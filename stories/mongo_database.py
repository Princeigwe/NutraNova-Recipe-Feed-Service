import os
from pymongo import MongoClient


connection_string = os.environ.get('MONGODB_NUTRANOVA_CLUSTER_CONNECTION_STRING')
nutranova_collections = os.environ.get('MONGODB_NUTRANOVA_CLUSTER_DATABASE_NAME')

client = MongoClient(connection_string)
database = client.nutranova_collections
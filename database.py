from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from config import settings


# Create a new client and connect to the server
client = MongoClient(settings.database_url, server_api=ServerApi('1'))

db = client.task_management_db
collection = db[settings.database_name]

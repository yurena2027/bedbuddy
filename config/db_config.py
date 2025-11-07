# Setup db information
from pymongo import MongoClient

# MongoDB Atlas connection string
MONGO_URI = "YOUR MONGO URI"
DB_NAME = "bedbuddy"

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

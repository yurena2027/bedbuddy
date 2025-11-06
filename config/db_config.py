# Setup db information
from pymongo import MongoClient

# MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://tkuga:f24pRi9tCIeq3kgO@main.do8aa5o.mongodb.net/"
DB_NAME = "bedbuddy"

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

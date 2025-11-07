# Setup db information
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# load variables from .env
load_dotenv()

# MongoDB Atlas connection string
#MONGO_URI = "YOUR MONGO URI"
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

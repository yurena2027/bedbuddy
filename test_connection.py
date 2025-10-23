import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

# Load your .env file
load_dotenv()
uri = os.getenv("MONGO_URI")

# Connect with TLS certificate check
client = MongoClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)

try:
    print("Connected to MongoDB:", client.server_info()["version"])
    print("Databases:", client.list_database_names())
except Exception as e:
    print("Connection failed:", e)


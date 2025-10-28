# FastAPI authentication backend for BedBuddy.
#
# This script connects to MongoDB Atlas using environment variables from a .env file,
# and exposes two endpoints:
#  • POST /auth/register  → Create new users
#  • POST /auth/login     → Authenticate and issue JWT tokens

# References:
# - Python Software Foundation. (2024). FastAPI documentation. 
#   https://fastapi.tiangolo.com/
# - MongoDB, Inc. (2025). PyMongo and Motor: Async MongoDB driver for Python. 
#   https://motor.readthedocs.io/
# - The Passlib Project. (2024). *Passlib: Password hashing framework for Python*. 
#   https://passlib.readthedocs.io/
# - Jose Library. (2024). *python-jose for JWT encoding/decoding*. GitHub repository.
#   https://github.com/mpdavis/python-jose

# ----------------------------
# Imports and setup
# ----------------------------
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient # from mongoDB wrapper for PyMongo, async
from dotenv import load_dotenv
import os
from security import hash_password, verify_password, create_access_token

load_dotenv()

# Initialize the FastAPI app
app = FastAPI(title="BedBuddy Authentication API")

# ----------------------------
# Database configuration
# ----------------------------
# Use the correct variable names from your .env file
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Create a MongoDB Atlas client and connect to the specific database
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]   # Example: bedbuddy
users = db["users"]    # Collection name "users"

# ----------------------------
# Request models
# ----------------------------
class UserCreds(BaseModel):
    username: str
    password: str

# ----------------------------
# Endpoints
# ----------------------------

@app.post("/auth/register", status_code=201)
async def register(body: UserCreds):
    """
    Register a new user.
    - Checks if username already exists
    - Hashes the password using bcrypt
    - Stores the user in MongoDB
    """
    # Check if user already exists
    if await users.find_one({"username": body.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password before storing
    hashed_pw = hash_password(body.password)
    
    # Insert new user record
    await users.insert_one({"username": body.username, "password_hash": hashed_pw})
    
    return {"msg": "User registered successfully."}


@app.post("/auth/login")
async def login(body: UserCreds):
    """
    Login an existing user.
    - Finds the username in MongoDB
    - Verifies the hashed password
    - Returns a signed JWT token if successful
    """
    user = await users.find_one({"username": body.username})
    
    # Handle invalid username or password
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Generate JWT token
    token = create_access_token(body.username)
    
    return {"access_token": token, "token_type": "bearer"}


# ----------------------------
# Quick notes
# ----------------------------
"""

# To test:
# uvicorn auth_api:app --reload
# Go to http://127.0.0.1:8000/docs

Expected endpoints:
    POST http://127.0.0.1:8000/auth/register
    POST http://127.0.0.1:8000/auth/login

Example test with curl:
    curl -X POST http://127.0.0.1:8000/auth/register 
         -H "Content-Type: application/json" 
         -d '{"username":"admin","password":"MyPass123!"}'

Example response:
    {"msg": "User registered successfully."}

Then login:
    {"access_token":"<token>","token_type":"bearer"}
"""

# --------------------------------------------
# Simple FastAPI authentication backend for BedBuddy
# --------------------------------------------
# This file creates two endpoints:
#   1. /auth/register  -> add a new user to MongoDB
#   2. /auth/login     -> verify username + password and return a JWT token
#
# We are using:
#   - FastAPI (web framework)
#   - Motor (async MongoDB driver)
#   - Passlib (for password hashing)
#   - python-jose (for JWT tokens)
#   - dotenv (to load secrets from .env)
# 
# References:
#     Davis, M. P. (2024). python-jose: JWT library for Python. GitHub repository. 
#           https://github.com/mpdavis/python-jose
#     Grinberg, M. (2023). JWT Authentication with Python. Real Python. 
#           https://realpython.com/token-based-authentication-with-flask/
#     MongoDB, Inc. (2025). Motor: Asynchronous Python driver for MongoDB. 
#           https://motor.readthedocs.io/
#     Python Software Foundation. (2024). FastAPI documentation. 
#           https://fastapi.tiangolo.com/
#     Python Software Foundation. (2024). dotenv — Python-dotenv library. 
#           https://pypi.org/project/python-dotenv/
#     The Passlib Project. (2024). Passlib: Password hashing framework for Python. 
#           https://passlib.readthedocs.io/

# ----------------------------
# Imports and setup
# ----------------------------
# FastAPI is the asynchronous web framework used for defining REST endpoints.
from fastapi import FastAPI, HTTPException
# Pydantic provides type validation for incoming request bodies.
from pydantic import BaseModel
# Motor is the asynchronous MongoDB driver maintained by MongoDB Inc.
from motor.motor_asyncio import AsyncIOMotorClient
# Load environment variables from the .env configuration file.
from dotenv import load_dotenv
import os

# Import the helper functions from security.py
from security import hash_password, verify_password, create_access_token

# Load environment variables (.env should be in the same folder)
load_dotenv()

# Create the FastAPI app
app = FastAPI(title="BedBuddy Auth API")

# Connect to MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Motor connects asynchronously, so we can use "await" when calling it
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
users = db["users"]  # collection where we store user data


# ----------------------------
# Define what kind of data we expect from the user
# ----------------------------
class UserCreds(BaseModel):
    username: str
    password: str


# ----------------------------
# Endpoint: Register
# ----------------------------
@app.post("/auth/register", status_code=201)
async def register(body: UserCreds):
    """
    Create a new user account.
    Steps:
      1. Check if username already exists.
      2. Hash the password.
      3. Save to MongoDB.
    """
    existing_user = await users.find_one({"username": body.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(body.password)
    await users.insert_one({
        "username": body.username,
        "password_hash": hashed_pw
    })
    return {"msg": "User registered successfully"}


# ----------------------------
# Endpoint: Login
# ----------------------------
@app.post("/auth/login")
async def login(body: UserCreds):
    """
    Log in an existing user.
    Steps:
      1. Find the user in the database.
      2. Verify password using bcrypt.
      3. If correct, create and return a JWT token.
    """
    user = await users.find_one({"username": body.username})

    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(body.username)
    return {"access_token": token, "token_type": "bearer"}


# ----------------------------
# How to test
# ----------------------------
"""
1. Run the API server:
   uvicorn auth_api:app --reload

2. In your browser, open:
   http://127.0.0.1:8000/docs

3. You'll see an automatic API tester.
   - Try POST /auth/register  →  make a new user
   - Try POST /auth/login     →  log in and see the token
"""

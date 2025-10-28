# --------------------------------------------
# Simple security utilities for BedBuddy Auth
# --------------------------------------------
# This file handles:
#   1. Password hashing and verification (bcrypt)
#   2. JWT token creation for login sessions
#
# It works together with auth_api.py
#
# Libraries used:
#   - Passlib (for secure password hashing)
#   - python-jose (for signing JWT tokens)
#   - dotenv (to load secrets like keys)
#
# References:
#     Davis, M. P. (2024). python-jose: JWT library for Python. 
#           https://github.com/mpdavis/python-jose
#     The Passlib Project. (2024). Passlib: Password hashing framework for Python. 
#           https://passlib.readthedocs.io/
#     Python Software Foundation. (2024). dotenv — Load environment variables. 
#           https://pypi.org/project/python-dotenv/
#     Python Software Foundation. (2024). datetime — Basic date and time types. 
#           https://docs.python.org/3/library/datetime.html

# ----------------------------
# Imports
# ----------------------------
from passlib.context import CryptContext      # handles bcrypt hashing
from jose import jwt                          # encodes/decodes JWT tokens
from datetime import datetime, timedelta      # to set expiration times
from dotenv import load_dotenv                # loads secrets from .env
import os                                     # to access environment variables

# ----------------------------
# Setup
# ----------------------------
# Load environment variables from the .env file
load_dotenv()

# Initialize bcrypt hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Read JWT settings from .env
SECRET_KEY = os.getenv("JWT_SECRET")           # secret key for signing tokens
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60              # 1-hour expiration


# ----------------------------
# Password functions
# ----------------------------
def hash_password(password: str) -> str:
    """
    Convert a plain password into a bcrypt hash.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain password matches a saved bcrypt hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ----------------------------
# Token functions
# ----------------------------
def create_access_token(username: str) -> str:
    """
    Create a JWT token that includes:
      - 'sub': username (subject)
      - 'exp': expiration time
    """
    expire_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire_time}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

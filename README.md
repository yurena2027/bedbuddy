# BedBuddy: ER Bed Management System
# Authors: BedBuddy Development Team (Fall 2025, UCCS CS 3300)
# Last Updated: 6 November 2025

The BedBuddy is a prototype desktop application built for emergency romm settings to track patients and bed availability. 
It combines a graphical interface created with Tkinter and a FastAPI backend that connects to a MongoDB Atlas cloud database. 

The application demonstrates secure login authentication, patient management, and bed assignmnet features using modular,
testable components.

<br>
# System Requirements:
Before running, ensure you hve the following:
1. Python 3.11 - 3.13 installed
2. MongoDB Atlas account (Database)
3. A working internet connection (to access Atlas cluster)

# Python Dependencies:
pip install fastapi uvicorn motor passlib[argon2] python-jose[cryptography] python-dotenv requests

# Packages used:
* FastAPI - backend framework (Tiangolo, 2025)
* Motor - async MongoDB driver (MongoDB Inc., 2025)
* passlib[argon2] - secure password hashing (The Passlib Project, 2024)
* Python-jose - JWT toekn generation (Davis, 2024)
* Python-dotenv - folr loading environmnet variables from local machine
* requests - sends HTTP POST requests from GUI Tkinter app to communicate with FastAPI server (Reitz & Chisamore, 2024)
* tkinter, ttk - Python's built in GUI toolkit (Python Software Foundation, 2025)

# Configuration:
Create a .env file in the /backend directory wit hyour own credentials to inlcude:

MONGO_URI=mongodb+srv://<your-cluster>
DB_NAME=bedbuddy
JWT_SECRET=<your-secret-key>
JWT_ALGORITHM=HS256

# How to test the code:

Step 1 - Start the Backend server

In your terminal:
  cd backend (ensure you are in this folder)
  uvicorn auth_appi:app --reload

You should see:
Uvicorn running on http://127.0.0.1:8000

***screenshot***

Step 2: Open Swagger UI
Go to http://127.0.0.1:8000/docs
FastAPI automatically generates a test interface where you can try both endpoints.
The endpoints you can test are:

  /auth/register         Register a new user      Returns 201 Created and "msg: User registered successfully"
  /auth/login            Log in exisitng user     Returns 200 ok and a JWT token
  /auth/login            Invalid credentials      Returns 401 Unauthorized with "Failed Login"

***Can we put screenshots***

Step 3 - Run the Tkinter Login app
Open a new terminal while keeping Uvicorn running:

  python LoginApp.py

  Enter the same credentials used in your registration test.

  ***Working on this Phase 2 today to ensure this actually works with no bugs***

Setp 4 - Verify Database update 
* This is phase 3 to be completed afoter frontend integration testing.hopefully i can get done today as well ***

# Summary:
  * Passwords are never stored in plain text
  * Each password is hashed using Argon2
  * The backend issues JWT tokens signed with the secret key defined in .env
  * Tokens are time-limited and must be reissued upon expiration
  * In a real healthcare setting, authentication and data privacy would comply
  with HIPPA / NIST SP 800-63B. The BedBuddy project incorporates this principels
  for demonstration and best practice learning. 

# Backend Code Overview:

auth_api.py

It defines two endpoints:
  * POST /auth/register - creates a uesr in MongoDB after hashing the password
  * POST /auth/login - verifies credentials and returns a JWT token

secrets.py

This code implements:
  * hash_password() and verify_password*) using Lasslib Argon2
  * create_access_token() using python-jose
  * Loads keys/secrets from .env using python-dotenv



<br>
# usage
Edit the **MONGO_URI** variable in **config/db_config.py**<br>
with your real MongoDB URI.


# References:

Davis, M. P. (2024). python-jose: JWT library for Python. GitHub. https://github.com/mpdavis/python-jose

MongoDB Inc. (2025). Motor: Asynchronous Python driver for MongoDB. https://motor.readthedocs.io

TkDocs. (2024). Tkinter Tutorial. https://tkdocs.com

The Passlib Project. (2024). Passlib: Password hashing framework for Python. https://passlib.readthedocs.io

Tiangolo, S. (2025). FastAPI documentation. https://fastapi.tiangolo.com

Python Software Foundation. (2025). tkinter — Python interface to Tcl/Tk. https://docs.python.org/3/library/tkinter.html

Python Software Foundation. (2025). os — Miscellaneous operating system interfaces. https://docs.python.org/3/library/os.html

Python Software Foundation. (2025). platform — Access to underlying platform data. https://docs.python.org/3/library/platform.html

Real Python. (2024). Python Tkinter Tutorial. https://realpython.com/python-gui-tkinter/

Reitz, K., & Chisamore, E. (2024). Requests: HTTP for Humans. https://requests.readthedocs.io

National Institute of Standards and Technology. (2020). Digital Identity Guidelines: Authentication and Lifecycle Management (NIST SP 800-63B). U.S. Department of Commerce. https://doi.org/10.6028/NIST.SP.800-63b

Sommerville, I. (2016). Software Engineering (10th ed.). Pearson Education.


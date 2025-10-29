# ==================================
# Hospital Bed Management – Login
# Tkinter GUI with FastAPI backend
# ==================================

# tkinter is pythons standard GUI library (Python Software Foundation, 2025a)
# ttk provides themed widgets; messagebox gives popup dialogs
# PhotoImage handles images like PNG/GIF/PPM formats

# -----Imports-------
# Tkinter core library for GUI 
import tkinter as tk
# ttk for themed widgets and messagebox for pop-ups
from tkinter import ttk, messagebox, PhotoImage
import platform # Detect Operating System (Python Software Foundation, 2025c)
import os       # File path utility (Python Software Foundation, 2025b)
import requests # For HTTP requests to FastAPI backend (Reitz & Chisamore, 2024)

# ------------------
# Login Window Class
# ------------------ 
# Define a Login class that inherits from Tkinter's root window (tk.Tk)
class Login(tk.Tk):
    '''GUI login window integrated with FastAPI authentication backend'''
    def __init__(self):
        ''' Initializes the login window layout and widget '''
        super().__init__()  # Initialize parent Tkroot window
        self.title("Bed Management – Login")  # Set window title
        self.geometry("400x350")              # Set window size
        self.resizable(False,False)           # Disable resizing

        # Cross-platform window icon (Python Software Foundation, 2025a)
        try:
            if platform.system() == "Windows":
                # Windows prefers .ico format
                self.iconbitmap("BBLogo.ico")
            else:
                # macOS/Linux fallback (PNG)
                self.iconphoto(False, PhotoImage(file="BBLogo.png"))
        except Exception as e:
            print("Icon not loaded:", e)

        # Create a frame with padding to hold the widgets
        frame = ttk.Frame(self, padding=16)
        # Expand to fill the window
        frame.pack(fill="both", expand=True)  

        # Get absolute path to current script's folder
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # Logo clickable test
        try:
            self.logo_img = PhotoImage(file=os.path.join(BASE_DIR, "BBLogo.png")) # load png logo
            self.logo_img = self.logo_img.subsample(8, 8)  # shrink by factor of 8
            logo_button = tk.Button(
                frame,
                image = self.logo_img,
                command = self.show_about, # clickable logo opens info
                borderwidth=0,
                highlightthickness=0
            )
            logo_button.grid(row=0, column=0, columnspan=2, pady=10)
        except Exception as e:
            print("Logo not found", e)

         # Username label and entry field
        ttk.Label(frame, text="username").grid(row=1, column=0, sticky="w")
        self.e_user = ttk.Entry(frame, width=26)  # Input box for username
        self.e_user.grid(row=1, column=1, pady=4)

        # Password label and entry field (hidden with • for security)
        ttk.Label(frame, text="password").grid(row=2, column=0, sticky="w")
        self.e_pass = ttk.Entry(frame, show="•", width=26)
        self.e_pass.grid(row=2, column=1, pady=4)

       # MFA (option and will not be connected) (NIST, 2020)
        self.lbl_mfa = ttk.Label(frame, text="MFA Code")
        self.e_mfa = ttk.Entry(frame, width=26)

        # Label for status/error messages (red text)
        self.status = ttk.Label(frame, text="", foreground="red")
        self.status.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 2))

        # "Sign In" button triggers do_login()
        ttk.Button(frame, text="Sign In", command=self.do_login).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )

        # Allow pressing Enter/Return to login
        self.bind("<Return>", lambda e: self.do_login())

        # Configure grid so both columns expand evenly
        for i in range(2):
            frame.grid_columnconfigure(i, weight=1)

    # Show the MFA input field if authentication backend requires it
    def show_mfa(self):
        self.lbl_mfa.grid(row=2, column=0, sticky="w")
        self.e_mfa.grid(row=2, column=1, pady=4)

    # Show an About dialog when logo is clicked
    def show_about(self):
        messagebox.showinfo("About", "Hospital Bed Management System\n" \
        "CS 3300 Project\nDeveloped by BedBuddy")

    # Main login logic: FastAPI Integration
    def do_login(self):
        ''' Attempt to log in a user through the FastAPI backend
            
            Steps:
            1. Read the username and password typed into the login form
            2. Send the data to the backend endpoints '/auth/login' using http POST
                (Reitz & Chisamore, 2024; Tiangolo, 2024)
            3. If backend confimrs login, display a success message and close the window
            4. If backend rejects login, display error message in red (Tiangolo, 2024)
            5. If backend cannot be reached, show a server error message 
            
        '''
        username = self.e_user.get().strip()  # Get the entered username (remove spaces)
        password = self.e_pass.get()          # Get the entered password
        
        try:
            ''' Send a request to the FastAPI backend at the /auth/login address
                We are using the HTTP "POST" method which means:
                - We are sending data to the server (username & password)
                - The server will process the data and give us a respionse
                (REitz & Chisamore, 2024; Tiangolo, 2024)
            '''
            response = requests.post("http://127.0.0.1:8000/auth/login", json={
                "username": username,   # Take the username. from the Tkinter form
                "password": password    # Take the password from the Tkinter form
            })

            # If the server responds with status code 200, it means login worked
            # (Tiangolo, 2025)
            if response.status_code == 200:
                # Convert the server's JSON reply into a Python dictionary
                data = response.json()

                # Get the "access_token" from the reply
                # This token is a JSON web token (JWT) used to prove you are logged in 
                # (Davis, 2024)
                access_token = data.get("access_token")

                # Show a success message in a Tkinter popup
                messagebox.showinfo("Success", "Login successful.")
                # Close the login window
                self.destroy()
            else: 
                # GUI first looks for the detail field returned by FastAPI. 
                # If it’s not there, it defaults to a generic message Login 
                # failed so users still see feedback (Tiangolo, 2025)
                error_message = response.json().get("detail", "Login failed")
                self.status.config(text=error_message) 
        
        # Handles cases like server down, no internet (Reitz & Chisamore, 2024)
        except requests.exceptions.RequestException as error:
            
# Entry point: run Login GUI
if __name__ == "__main__":
    Login().mainloop()

'''
References:
Davis, M. P. (2024). python-jose: JWT library for Python. GitHub. 
    https://github.com/mpdavis/python-jose
Jose project team. (2024). PyJWT documentation. PyJWT. 
    https://pyjwt.readthedocs.io/
National Institute of Standards and Technology. (2020). Digital 
    identity guidelines: Authentication and lifecycle management 
(NIST Special Publication 800-63B). U.S. Department of Commerce. 
    https://doi.org/10.6028/NIST.SP.800-63b
Python Software Foundation. (2025, October 29). tkinter — Python 
    interface to Tcl/Tk. In Python 3.13 documentation. 
    https://docs.python.org/3/library/tkinter.html
Python Software Foundation. (2025, October 29). os — Miscellaneous 
    operating system interfaces. In Python 3.13 documentation. 
    https://docs.python.org/3/library/os.html
Python Software Foundation. (2025, October 29). platform — Access 
    to underlying platform’s identifying data. In Python 3.13 documentation. 
    https://docs.python.org/3/library/platform.html
Reitz, K., & Chisamore, E. (2024). Requests: HTTP for humans. 
    Python Requests. https://requests.readthedocs.io/
Tiangolo, S. (2025). FastAPI documentation. FastAPI. 
    https://fastapi.tiangolo.com/
'''
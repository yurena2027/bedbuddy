# ==================================
# Hospital Bed Management – Login
# Class-based design with MFA + logo
# ==================================

# tkinter is pythons standard GUI library
# ttk provides themed widgets
# messagebox gives popup dialogs
# PhotoImage handles images like PNG/GIF/PPM

# Import Tkinter core library for GUI
import tkinter as tk
# Import ttk for themed widgets and messagebox for pop-ups
from tkinter import ttk, messagebox, PhotoImage
# Import authentication backend and role management
# from auth_backend import authenticate, get_user_roles
# Import hospital bed management launcher (opens after login)
#from bed_management import launch_bed_management
import platform # Detect OS
import os

# Define a Login class that inherits from Tkinter's root window (tk.Tk)
class Login(tk.Tk):
    def __init__(self):
        super().__init__()  # Initialize parent Tkroot window
        self.title("Bed Management – Login")  # Set window title
        self.geometry("400x350")  # Set window size
        self.resizable(False,False)  # Disable resizing

        # Cross-platform window icon
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
                command = self.show_about, # clickalbe logo opens info
                borderwidth=0,
                highlightthickness=0
            )
            logo_button.grid(row=0, column=0, columnspan=2, pady=10)
        except Exception as e:
            print("Logo not found", e)

         # Username label and entry field
        ttk.Label(frame, text="Username").grid(row=1, column=0, sticky="w")
        self.e_user = ttk.Entry(frame, width=26)  # Input box for username
        self.e_user.grid(row=1, column=1, pady=4)

        # Password label and entry field (hidden with • for security)
        ttk.Label(frame, text="Password").grid(row=2, column=0, sticky="w")
        self.e_pass = ttk.Entry(frame, show="•", width=26)
        self.e_pass.grid(row=2, column=1, pady=4)

       # Prepare MFA label and entry but do not display until required
        self.lbl_mfa = ttk.Label(frame, text="MFA Code")
        self.e_mfa = ttk.Entry(frame, width=26)

        # Label for status/error messages (red text)
        self.status = ttk.Label(frame, text="", foreground="red")
        self.status.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 2))

        # "Sign In" button triggers do_login()
        ttk.Button(frame, text="Sign In", command=self.do_login).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )

        # Bind Enter/Return key to also trigger login
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
        messagebox.showinfo("About", "Hospital Bed Management System\nVersion 1.0")

    # Main login logic
    def do_login(self):
        u = self.e_user.get().strip()  # Get username (remove spaces)
        p = self.e_pass.get()  # Get password
        # Get MFA if the field is visible, otherwise None
        mfa = self.e_mfa.get().strip() if self.e_mfa.winfo_ismapped() else None
        
        # --- Temporary logic for testing GUI only ---
        if u == "admin" and p == "password":  
            messagebox.showinfo("Login Success", f"Welcome {u}! (stubbed, no DB yet)")
            self.destroy()
            # later: launch_bed_management(u, roles)
        else:
            self.status.config(text="Invalid username or password") 
        
        # Call backend authentication once this is set up (see the above for testing)
        #ok, user_id, msg = authenticate(u, p, mfa)
        #if not ok:  # If login failed
        #    if msg == "MFA code required.":  # If MFA is needed
        #        self.status.config(text="Enter your 6-digit MFA code.")
        #       self.show_mfa()  # Reveal MFA field
        #    else:
        #        self.status.config(text=msg)  # Show error message
        #    return

         # On success: launch bed management and close login
        #roles = get_user_roles(u)
        #messagebox.showinfo("Login Success", f"Welcome {u}! Role: {roles}")
        #self.destroy()
        #launch_bed_management(u, roles)

        # On success: show messagebox and close login window
        messagebox.showinfo("Success", "Login successful.")
        self.destroy()

# Entry point: run Login GUI
if __name__ == "__main__":
    Login().mainloop()

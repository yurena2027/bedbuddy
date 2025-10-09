import tkinter as tk  # Import the main Tkinter library for creating GUI windows and widgets
from tkinter import ttk  # Import ttk for themed widgets like Treeview

root = tk.Tk()  # Create the main application window
root.title("Hospital Dashboard")  # Set the window title
root.geometry("1000x450")  # Set the size of the window (width x height in pixels)

# ---------------- Left Sidebar ---------------- #
sidebar = tk.Frame(root, bg="lightgray", width=150)  # Create a sidebar frame with gray background
sidebar.pack(side="left", fill="y")  # Pack the sidebar on the left side and fill it vertically

# Sidebar Labels
myed_label = tk.Label(sidebar, text="ED Space", bg="lightgray", font=("Arial", 10, "bold"))  # Label for ED space
myed_label.pack(anchor="w", padx=10, pady=(10, 0))  # Pack label to left with padding

# ---------------- Patient View ---------------- #
patient_frame = tk.Frame(root, bd=1, relief="solid")  # Create a frame for Patient View with border
patient_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)  # Pack frame to left and fill space

patient_label = tk.Label(patient_frame, text="Patient View", font=("Arial", 12, "bold"))  # Label for Patient View
patient_label.pack(anchor="w", padx=5, pady=5)  # Pack label at top-left with padding

# Treeview for Patient Table
columns = ("Name", "Location", "Patient Info")  # Define columns for patient data
tree = ttk.Treeview(patient_frame, columns=columns, show="headings", height=10)  # Create Treeview widget

for col in columns:
    tree.heading(col, text=col)  # Set the header text for each column
    tree.column(col, anchor="center", width=150)  # Set column width and center alignment

tree.pack(fill="both", expand=True, padx=10, pady=10)  # Pack the Treeview in the patient frame

# ---------------- Bay View ---------------- #
bay_frame = tk.Frame(root, bd=1, relief="solid", width=300)  # Create a frame for Bay View with border
bay_frame.pack(side="left", fill="both", padx=5, pady=5)  # Pack frame to left and fill available space

bay_label = tk.Label(bay_frame, text="Bay View", font=("Arial", 12, "bold"))  # Label for Bay View
bay_label.pack(anchor="w", padx=5, pady=5)  # Pack label at top-left

beds_frame = tk.Frame(bay_frame, bg="lightgray")  # Frame inside bay_frame to hold beds
beds_frame.pack(fill="both", expand=True, padx=20, pady=20)  # Fill space and add padding

# ---------------- Data ---------------- #
bay_beds = {  # Dictionary storing bay information and bed data
    1: [  # Bay 1 beds
        ("B1", "yellow", True, "John Green"),  # Bed name, color, patient presence, patient name
        ("B2", "yellow", True, "Brandon Sanderson"),
        ("B3", "white", False, None),
        ("B4", "yellow", True, "George RR Martin"),
        ("B5", "white", False, None)
    ],
    2: [  # Bay 2 beds
        ("B1", "yellow", True, "Rick Riordan"),
        ("B2", "white", False, None),
        ("B3", "white", False, None),
        ("B4", "yellow", True, "Frank Herbert")
    ]
}

# ---------------- Global Variable ---------------- #
selected_bed = None  # Track which bed is currently selected (for red border highlight)

# ---------------- Functions ---------------- #
def show_patients(bay_number):
    """Display patients for a specific bay in the Treeview"""
    for row in tree.get_children():  # Delete all existing rows in Treeview
        tree.delete(row)
    for b in bay_beds.get(bay_number, []):  # Loop through beds in the bay
        bedname, color, has_patient, pname = b  # Unpack bed info
        if has_patient and color in ("yellow", "orange"):  # Only show beds with patients
            location = f"Bay {bay_number} / {bedname}"  # Format location string
            tree.insert("", "end", values=(pname, location, "..."))  # Insert patient info into Treeview

def create_bed(frame, text, color="white", icon=False, patient_name=None, bay_number=None):
    """Create a bed block with optional patient icon and click event"""
    global selected_bed  # Use the global variable to track selection

    f = tk.Frame(frame, width=80, height=100, bg="white", bd=1, relief="solid")  # Create frame for bed
    f.propagate(False)  # Prevent child widgets from resizing the frame
    f.pack_propagate(False)  # Prevent automatic resizing by packing

    label = tk.Label(f, text=text, bg="white", font=("Arial", 10))  # Label with bed name
    label.pack(side="bottom", pady=5)  # Place bed label at bottom

    if icon:  # If a patient icon should be displayed
        icon_lbl = tk.Label(f, text="👤", fg=color, bg="darkgray", font=("Arial", 25))  # Create icon label
        icon_lbl.pack(side="top", pady=5)  # Place icon at top

    # Click event to highlight the bed and optionally show patient in Treeview
    def on_click(event):
        global selected_bed
        if selected_bed is not None:  # Remove red border from previous selection
            selected_bed.config(bd=1, relief="solid", highlightthickness=0)
        f.config(bd=3, relief="solid", highlightbackground="red", highlightcolor="red", highlightthickness=3)  # Highlight current bed
        selected_bed = f  # Update global selected bed

        if patient_name:  # Update Treeview to show patient info
            for row in tree.get_children():  # Clear previous Treeview rows
                tree.delete(row)
            location = f"Bay {bay_number} / {text}"  # Format bed location
            tree.insert("", "end", values=(patient_name, location, "..."))  # Insert patient info

    f.bind("<Button-1>", on_click)  # Bind click event to bed frame
    if icon:  # Bind click event to icon too
        icon_lbl.bind("<Button-1>", on_click)

    return f  # Return the bed frame widget

def show_bay(bay_number):
    """Display all beds for a given bay"""
    global selected_bed

    if selected_bed is not None:  # Clear previous selection
        selected_bed.config(bd=1, relief="solid", highlightthickness=0)
        selected_bed = None

    for row in tree.get_children():  # Clear Treeview
        tree.delete(row)

    for widget in beds_frame.winfo_children():  # Destroy previous bed widgets
        widget.destroy()

    beds = bay_beds.get(bay_number, [])  # Get beds for the bay
    row, col = 0, 0  # Initialize grid row/column
    for b in beds:
        bedname, color, has_patient, pname = b
        bed = create_bed(
            beds_frame, bedname, color, has_patient,
            patient_name=pname, bay_number=bay_number
        )
        bed.grid(row=row, column=col, padx=15, pady=15)  # Place bed in grid
        col += 1
        if col > 2:  # Move to next row after 3 columns
            col = 0
            row += 1

    show_patients(bay_number)  # Display patients in Treeview for this bay

# Sidebar Bay buttons
bay1_btn = tk.Button(sidebar, text="- Bay 1", bg="lightgray", relief="flat", command=lambda: show_bay(1))  # Button to show Bay 1
bay1_btn.pack(anchor="w", padx=20)  # Pack button to left

bay2_btn = tk.Button(sidebar, text="- Bay 2", bg="lightgray", relief="flat", command=lambda: show_bay(2))  # Button to show Bay 2
bay2_btn.pack(anchor="w", padx=20)  # Pack button

# Show all patients button
def show_all_patients():
    """Display all patients from all bays in the Treeview"""
    for row in tree.get_children():  # Clear Treeview
        tree.delete(row)
    for bay_num, beds in bay_beds.items():  # Loop through all bays
        for b in beds:
            bedname, color, has_patient, pname = b
            if has_patient and color in ("yellow", "orange"):  # Only show patients
                location = f"Bay {bay_num} / {bedname}"  # Format location
                tree.insert("", "end", values=(pname, location, "..."))  # Insert patient info

patients_btn = tk.Button(sidebar, text="Show All Patients", relief="flat", bg="gray25", fg="white",
                         command=show_all_patients)  # Button to show all patients
patients_btn.pack(anchor="w", padx=10, pady=20, fill="x")  # Pack button

# Load Bay1 by default
show_bay(1)  # Display Bay 1 on startup

root.mainloop()  # Start the Tkinter main event loop
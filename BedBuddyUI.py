import tkinter as tk  # Import the main Tkinter library for creating GUI windows and widgets
from tkinter import ttk, simpledialog, messagebox  # Import ttk for themed widgets, dialogs, and message boxes

root = tk.Tk()  # Create the main application window
root.title("Hospital Dashboard")  # Set the window title
root.geometry("1400x450")  # Set the window size (width x height)

# ---------------- Left Sidebar ---------------- #
sidebar = tk.Frame(root, bg="lightgray", width=150)  # Sidebar frame on the left
sidebar.pack(side="left", fill="y")  # Pack sidebar to left and fill vertically

# Sidebar Label
myed_label = tk.Label(sidebar, text="ED Space", bg="lightgray", font=("Arial", 10, "bold"))
myed_label.pack(anchor="w", padx=10, pady=(10, 0))  # Top-left label in sidebar

# ---------------- Patient View ---------------- #
patient_frame = tk.Frame(root, bd=1, relief="solid")  # Frame for patient list
patient_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

patient_label = tk.Label(patient_frame, text="Patient View", font=("Arial", 12, "bold"))
patient_label.pack(anchor="w", padx=5, pady=5)  # Label at top-left of patient frame

# Treeview for displaying patients
columns = ("Name", "Location", "Patient Info")  # Define table columns
tree = ttk.Treeview(patient_frame, columns=columns, show="headings", height=10)

for col in columns:
    tree.heading(col, text=col)  # Set column headings
    tree.column(col, anchor="center", width=150)  # Set column width and center alignment

tree.pack(fill="both", expand=True, padx=10, pady=10)  # Pack Treeview into patient frame

# ---------------- Bay View ---------------- #
bay_frame = tk.Frame(root, bd=1, relief="solid", width=300)  # Frame for Bay View
bay_frame.pack(side="left", fill="both", padx=5, pady=5)

bay_label = tk.Label(bay_frame, text="Bay View", font=("Arial", 12, "bold"))
bay_label.pack(anchor="w", padx=5, pady=5)  # Label at top-left of bay frame

beds_frame = tk.Frame(bay_frame, bg="lightgray")  # Frame to hold bed widgets
beds_frame.pack(fill="both", expand=True, padx=20, pady=20)

# ---------------- Data ---------------- #
bay_beds = {  # Dictionary storing bay and bed information
    1: [
        ("B1", "yellow", True, "John Green"),
        ("B2", "yellow", True, "Brandon Sanderson"),
        ("B3", "white", False, None),
        ("B4", "yellow", True, "George RR Martin"),
        ("B5", "white", False, None)
    ],
    2: [
        ("B1", "yellow", True, "Rick Riordan"),
        ("B2", "white", False, None),
        ("B3", "white", False, None),
        ("B4", "yellow", True, "Frank Herbert")
    ]
}

# ---------------- Global Variable ---------------- #
selected_bed = None  # Track currently selected bed for highlight
current_bay = 1      # Track currently displayed bay (None = all bays view)

# ---------------- Functions ---------------- #
def refresh_tree(bay_filter=None):
    """Refresh the patient list in Treeview, optionally filtered by bay."""
    for row in tree.get_children():  # Clear existing rows
        tree.delete(row)

    if bay_filter is not None:
        bays_to_show = [bay_filter]  # Single bay view
    else:
        bays_to_show = bay_beds.keys()  # All bays view

    for bay_num in bays_to_show:
        for bedname, color, has_patient, pname in bay_beds[bay_num]:
            if has_patient:
                location = f"Bay {bay_num} / {bedname}"  # Format location string
                tree.insert("", "end", values=(pname, location, "..."))

def update_bed_info(bay_number, bedname, color, has_patient, pname):
    """Update information for a specific bed."""
    for i, (bname, _, _, _) in enumerate(bay_beds[bay_number]):
        if bname == bedname:
            bay_beds[bay_number][i] = (bname, color, has_patient, pname)
            break

def create_bed(frame, bed_info, bay_number):
    """Create an interactive bed widget with optional patient icon and click event."""
    global selected_bed

    bedname, color, has_patient, pname = bed_info
    f = tk.Frame(frame, width=80, height=100, bg="white", bd=1, relief="solid")
    f.pack_propagate(False)  # Prevent frame from resizing automatically

    # Bed name label
    label = tk.Label(f, text=bedname, bg="white", font=("Arial", 10))
    label.pack(side="bottom", pady=5)

    icon_lbl = None
    if has_patient:  # Show patient icon if bed occupied
        icon_lbl = tk.Label(f, text="👤", fg=color, bg="darkgray", font=("Arial", 25))
        icon_lbl.pack(side="top", pady=5)

    def on_click(event):
        """Handle bed click: add or remove a patient, highlight selection."""
        global selected_bed

        # Highlight selected bed
        if selected_bed is not None:
            selected_bed.config(bd=1, relief="solid", highlightthickness=0)
        f.config(bd=3, relief="solid", highlightbackground="red",
                 highlightcolor="red", highlightthickness=3)
        selected_bed = f

        # Get current bed info
        _, curr_color, curr_has_patient, curr_name = next(b for b in bay_beds[bay_number] if b[0] == bedname)

        if curr_has_patient:
            remove = messagebox.askyesno("Remove Patient", f"Remove {curr_name} from {bedname}?")
            if remove:
                update_bed_info(bay_number, bedname, "white", False, None)
                # Keep correct view after removal
                if current_bay is None:
                    show_all_bays()
                else:
                    show_bay(current_bay)
                refresh_tree(current_bay)
        else:
            pname_input = simpledialog.askstring("Add Patient", f"Enter patient name for {bedname}:")
            if pname_input:
                update_bed_info(bay_number, bedname, "yellow", True, pname_input)
                if current_bay is None:
                    show_all_bays()
                else:
                    show_bay(current_bay)
                refresh_tree(current_bay)

    # Bind click events
    f.bind("<Button-1>", on_click)
    label.bind("<Button-1>", on_click)
    if icon_lbl:
        icon_lbl.bind("<Button-1>", on_click)

    return f

def show_bay(bay_number):
    """Display all beds for a specific bay."""
    global selected_bed, current_bay
    current_bay = bay_number

    if selected_bed is not None:  # Clear previous selection highlight
        selected_bed.config(bd=1, relief="solid", highlightthickness=0)
        selected_bed = None

    # Clear previous bed widgets
    for widget in beds_frame.winfo_children():
        widget.destroy()

    # Layout beds in grid
    row, col = 0, 0
    for bed_info in bay_beds[bay_number]:
        bed = create_bed(beds_frame, bed_info, bay_number)
        bed.grid(row=row, column=col, padx=15, pady=15)
        col += 1
        if col > 2:
            col = 0
            row += 1

    refresh_tree(bay_number)  # Update patient Treeview for this bay

def show_all_bays():
    """Display all bays side by side with a divider."""
    global selected_bed, current_bay
    current_bay = None  # All Bays view

    if selected_bed is not None:
        selected_bed.config(bd=1, relief="solid", highlightthickness=0)
        selected_bed = None

    # Clear previous bed widgets
    for widget in beds_frame.winfo_children():
        widget.destroy()

    # Configure 3-column layout: Bay1 | Divider | Bay2
    beds_frame.columnconfigure(0, weight=1)
    beds_frame.columnconfigure(1, weight=0)
    beds_frame.columnconfigure(2, weight=1)
    beds_frame.rowconfigure(0, weight=1)

    # Bay 1 frame
    bay1_frame = tk.Frame(beds_frame, bd=1, relief="solid", padx=10, pady=10)
    bay1_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

    # Divider between bays
    divider = tk.Frame(beds_frame, width=3, bg="black")
    divider.grid(row=0, column=1, sticky="ns")

    # Bay 2 frame
    bay2_frame = tk.Frame(beds_frame, bd=1, relief="solid", padx=10, pady=10)
    bay2_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))

    # Populate Bay 1 beds
    for i, bed_info in enumerate(bay_beds[1]):
        row, col = divmod(i, 3)
        bed = create_bed(bay1_frame, bed_info, 1)
        bed.grid(row=row, column=col, padx=15, pady=15)

    # Populate Bay 2 beds
    for i, bed_info in enumerate(bay_beds[2]):
        row, col = divmod(i, 3)
        bed = create_bed(bay2_frame, bed_info, 2)
        bed.grid(row=row, column=col, padx=15, pady=15)

    refresh_tree(None)  # Refresh patient list to show all bays

# ---------------- Sidebar Buttons ---------------- #
bay1_btn = tk.Button(sidebar, text="- Bay 1", bg="lightgray", relief="flat", command=lambda: show_bay(1))
bay1_btn.pack(anchor="w", padx=20)

bay2_btn = tk.Button(sidebar, text="- Bay 2", bg="lightgray", relief="flat", command=lambda: show_bay(2))
bay2_btn.pack(anchor="w", padx=20)

patients_btn = tk.Button(sidebar, text="Show All Patients", relief="flat", bg="gray25", fg="white", command=show_all_bays)
patients_btn.pack(anchor="w", padx=10, pady=20, fill="x")

# ---------------- Default Load ---------------- #
show_bay(1)  # Load Bay 1 by default

root.mainloop()  # Start Tkinter main loop

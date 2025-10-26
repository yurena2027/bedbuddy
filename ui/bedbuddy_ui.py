
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

root = tk.Tk()
root.title("Hospital Dashboard")
root.geometry("1500x450")

# ---------------- Left Sidebar ---------------- #
sidebar = tk.Frame(root, bg="lightgray", width=150)
sidebar.pack(side="left", fill="y")

# Sidebar Label
myed_label = tk.Label(sidebar, text="ED Space", bg="lightgray", font=("Arial", 10, "bold"))
myed_label.pack(anchor="w", padx=10, pady=(10, 0))

# ---- Frame to hold bay buttons ---- #
bay_buttons_frame = tk.Frame(sidebar, bg="lightgray")
bay_buttons_frame.pack(anchor="w", padx=10, pady=10, fill="x")

# ---------------- Patient View ---------------- #
patient_frame = tk.Frame(root, bd=1, relief="solid")
patient_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

patient_label = tk.Label(patient_frame, text="Patient View", font=("Arial", 12, "bold"))
patient_label.pack(anchor="w", padx=5, pady=5)

columns = ("Name", "Location", "Patient Info")
tree = ttk.Treeview(patient_frame, columns=columns, show="headings", height=10)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=150)

tree.pack(fill="both", expand=True, padx=10, pady=10)

# ---------------- Bay View ---------------- #
bay_frame = tk.Frame(root, bd=1, relief="solid", width=250)
bay_frame.pack(side="left", fill="both", padx=5, pady=5)

bay_label = tk.Label(bay_frame, text="Bay View", font=("Arial", 12, "bold"))
bay_label.pack(anchor="w", padx=5, pady=5)

beds_frame = tk.Frame(bay_frame, bg="lightgray")
beds_frame.pack(fill="both", expand=True, padx=20, pady=20)

# ---------------- Data ---------------- #
bay_beds = {
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

# ---------------- Global Variables ---------------- #
selected_bed = None
current_bay = 1
MAX_BAYS = 3
MAX_BEDS_PER_BAY = 6

# ---------------- Functions ---------------- #
def refresh_tree(bay_filter=None):
    for row in tree.get_children():
        tree.delete(row)

    if bay_filter is not None:
        bays_to_show = [bay_filter]
    else:
        bays_to_show = bay_beds.keys()

    for bay_num in bays_to_show:
        for bedname, color, has_patient, pname in bay_beds[bay_num]:
            if has_patient:
                location = f"Bay {bay_num} / {bedname}"
                tree.insert("", "end", values=(pname, location, "..."))

def update_bed_info(bay_number, bedname, color, has_patient, pname):
    for i, (bname, _, _, _) in enumerate(bay_beds[bay_number]):
        if bname == bedname:
            bay_beds[bay_number][i] = (bname, color, has_patient, pname)
            break

def create_bed(frame, bed_info, bay_number):
    global selected_bed
    bedname, color, has_patient, pname = bed_info
    f = tk.Frame(frame, width=70, height=90, bg="white", bd=1, relief="solid")
    f.pack_propagate(False)

    label = tk.Label(f, text=bedname, bg="white", font=("Arial", 10))
    label.pack(side="bottom", pady=5)

    icon_lbl = None
    if has_patient:
        icon_lbl = tk.Label(f, text="👤", fg=color, bg="darkgray", font=("Arial", 25))
        icon_lbl.pack(side="top", pady=5)

    def on_click(event):
        global selected_bed
        if selected_bed is not None:
            selected_bed.config(bd=1, relief="solid", highlightthickness=0)
        f.config(bd=3, relief="solid", highlightbackground="red", highlightcolor="red", highlightthickness=3)
        selected_bed = f

        _, curr_color, curr_has_patient, curr_name = next(b for b in bay_beds[bay_number] if b[0] == bedname)

        if curr_has_patient:
            remove = messagebox.askyesno("Remove Patient", f"Remove {curr_name} from {bedname}?")
            if remove:
                update_bed_info(bay_number, bedname, "white", False, None)
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

    f.bind("<Button-1>", on_click)
    label.bind("<Button-1>", on_click)
    if icon_lbl:
        icon_lbl.bind("<Button-1>", on_click)

    return f

# ---------------- Show Specific Bay ---------------- #
def show_bay(bay_number):
    global selected_bed, current_bay
    current_bay = bay_number
    if selected_bed is not None:
        selected_bed.config(bd=1, relief="solid", highlightthickness=0)
        selected_bed = None

    # Show Add Bed button
    add_bed_btn.pack(side="bottom", fill="x", pady=5)

    for widget in beds_frame.winfo_children():
        widget.destroy()

    row, col = 0, 0
    for bed_info in bay_beds[bay_number]:
        bed = create_bed(beds_frame, bed_info, bay_number)
        bed.grid(row=row, column=col, padx=15, pady=15)
        col += 1
        if col > 2:  # wrap beds to next row after 3
            col = 0
            row += 1

    bay_label_under = tk.Label(beds_frame, text=f"Bay {bay_number}", font=("Arial", 10, "bold"), bg="lightgray")
    bay_label_under.grid(row=row+1, column=0, columnspan=3, pady=(0,10))

    refresh_tree(bay_number)

# ---------------- Show All Bays / Patients ---------------- #
def show_all_bays():
    global selected_bed, current_bay
    current_bay = None
    if selected_bed is not None:
        selected_bed.config(bd=1, relief="solid", highlightthickness=0)
        selected_bed = None

    # Hide Add Bed button in all patients view
    add_bed_btn.pack_forget()

    for widget in beds_frame.winfo_children():
        widget.destroy()

    bays_per_row = 3
    sorted_bays = sorted(bay_beds.items())
    for idx, (bay_num, beds) in enumerate(sorted_bays):
        row = (idx // bays_per_row) * 2
        col = idx % bays_per_row

        bay_container = tk.Frame(beds_frame, bd=1, relief="solid", padx=5, pady=5)
        bay_container.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # Wrap beds inside bay
        for j, bed_info in enumerate(beds):
            bed_row, bed_col = divmod(j, 3)
            bed = create_bed(bay_container, bed_info, bay_num)
            bed.grid(row=bed_row, column=bed_col, padx=5, pady=5)

        bay_label_under = tk.Label(beds_frame, text=f"Bay {bay_num}", font=("Arial", 10, "bold"), bg="lightgray")
        bay_label_under.grid(row=row+1, column=col, pady=(0,5))

        beds_frame.columnconfigure(col, weight=1)
    for r in range(((len(sorted_bays) + bays_per_row - 1) // bays_per_row) * 2):
        beds_frame.rowconfigure(r, weight=1)

    refresh_tree(None)

# ---------------- Add Bay Function ---------------- #
def add_bay():
    total_bays = len(bay_beds)
    if total_bays >= MAX_BAYS:
        messagebox.showwarning("Limit Reached", f"Maximum of {MAX_BAYS} bays reached!")
        return

    bay_num = total_bays + 1
    bay_beds[bay_num] = [(f"B{i+1}", "white", False, None) for i in range(3)]

    new_btn = tk.Button(bay_buttons_frame, text=f"- Bay {bay_num}", bg="lightgray", relief="flat",
                        command=lambda num=bay_num: show_bay(num))
    new_btn.pack(anchor="w", padx=5)

    messagebox.showinfo("Success", f"Bay {bay_num} added successfully!")
    if current_bay is None:
        show_all_bays()

# ---------------- Add Bed Function ---------------- #
def add_bed():
    global current_bay
    if current_bay is None:
        messagebox.showwarning("No Bay Selected", "Please select a specific bay to add a bed.")
        return

    beds_in_bay = bay_beds[current_bay]
    if len(beds_in_bay) >= MAX_BEDS_PER_BAY:
        messagebox.showwarning("Limit Reached", f"Bay {current_bay} can only have {MAX_BEDS_PER_BAY} beds.")
        return

    new_bed_name = f"B{len(beds_in_bay)+1}"
    beds_in_bay.append((new_bed_name, "white", False, None))
    show_bay(current_bay)

# ---------------- Sidebar Buttons ---------------- #
bay1_btn = tk.Button(bay_buttons_frame, text="- Bay 1", bg="lightgray", relief="flat", command=lambda: show_bay(1))
bay1_btn.pack(anchor="w", padx=5)

bay2_btn = tk.Button(bay_buttons_frame, text="- Bay 2", bg="lightgray", relief="flat", command=lambda: show_bay(2))
bay2_btn.pack(anchor="w", padx=5)

patients_btn = tk.Button(sidebar, text="Show All Patients", relief="flat", bg="gray25", fg="white", command=show_all_bays)
patients_btn.pack(anchor="w", padx=5, pady=5, fill="x")

add_bay_btn = tk.Button(sidebar, text="+ Add Bay", bg="lightblue", relief="raised", command=add_bay)
add_bay_btn.pack(side="bottom", fill="x", pady=5)

# Add Bed button created but packed dynamically
add_bed_btn = tk.Button(sidebar, text="+ Add Bed", bg="lightgreen", relief="raised", command=add_bed)

# ---------------- Default Load ---------------- #
show_bay(1)

root.mainloop()

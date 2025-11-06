import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from database.patient import Patient
from config.db_config import get_db
from database.db_operation import Database

database = Database(get_db())

MAX_BAYS = 6
MAX_BEDS_PER_BAY = 6

class BedBuddy:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hospital Dashboard")
        self.root.geometry("1500x450")

        # ---------------- Data ---------------- #
        self.bay_beds: dict[int, list[Patient]] = {}
        self.load_db_bays()

        # ---------------- State ---------------- #
        self.selected_bed = None
        self.current_bay = 1

        # ---------------- UI Setup ---------------- #
        self.setup_sidebar()
        self.setup_patient_view()
        self.setup_bay_view()
        self.show_bay(1)

    # ---------------- Initial Data Loading Method ---------------- #
    def load_db_bays(self) -> dict[int, list[Patient]]:
        bays = [int(bay) for bay in database.db.list_collection_names() if bay.isdigit()]
        priority_colors = {"High": "red", "Medium": "orange", "Low": "green"}

        for bay in bays:
            patients = database.get_bay_patients(bay)  # returns list[Patient]
            # Assign color based on priority if not set
            for patient in patients:
                if not getattr(patient, "color", None):
                    patient.color = priority_colors.get(getattr(patient, "priority", "Medium"), "deeppink2")
            self.bay_beds[bay] = patients
        return self.bay_beds

    # ---------------- Setup Methods ---------------- #
    def setup_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg="lightgray", width=150)
        self.sidebar.pack(side="left", fill="y")

        myed_label = tk.Label(self.sidebar, text="ED Space", bg="lightgray", font=("Arial", 10, "bold"))
        myed_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.bay_buttons_frame = tk.Frame(self.sidebar, bg="lightgray")
        self.bay_buttons_frame.pack(anchor="w", padx=10, pady=10, fill="x")

        for i in range(1, len(self.bay_beds)+1):
            btn = tk.Button(self.bay_buttons_frame, text=f"- Bay {i}", bg="lightgray", relief="flat",
                            command=lambda num=i: self.show_bay(num))
            btn.pack(anchor="w", padx=5)

        self.patients_btn = tk.Button(self.sidebar, text="Show All Patients", relief="flat", bg="gray25", fg="white",
                                      command=self.show_all_bays)
        self.patients_btn.pack(anchor="w", padx=5, pady=5, fill="x")

        self.bay_control_frame = tk.Frame(self.sidebar, bd=1, relief="groove", bg="lightgray", padx=5, pady=5)
        self.bay_control_frame.pack(side="bottom", fill="x", pady=5)

        self.add_bay_btn = tk.Button(self.bay_control_frame, text="+ Add Bay", bg="lightblue", relief="raised",
                                     command=self.add_bay)
        self.remove_bay_btn = tk.Button(self.bay_control_frame, text="- Remove Bottom Bay", bg="red", fg="white",
                                        relief="raised", command=self.remove_bay)
        self.add_bay_btn.pack(fill="x", pady=(0,5))
        self.remove_bay_btn.pack(fill="x", pady=(5,0))

        self.bed_control_frame = tk.Frame(self.sidebar, bd=1, relief="groove", bg="lightgray", padx=5, pady=5)
        self.add_bed_btn = tk.Button(self.bed_control_frame, text="+ Add Bed", bg="lightgreen", relief="raised",
                                     command=self.add_bed)
        self.remove_bed_btn = tk.Button(self.bed_control_frame, text="- Remove Bed", bg="salmon", relief="raised",
                                        command=self.remove_bed)
        self.add_bed_btn.pack(fill="x", pady=(0,2))
        self.remove_bed_btn.pack(fill="x", pady=(2,0))

    def setup_patient_view(self):
        self.patient_frame = tk.Frame(self.root, bd=1, relief="solid")
        self.patient_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        patient_label = tk.Label(self.patient_frame, text="Patient View", font=("Arial", 12, "bold"))
        patient_label.pack(anchor="w", padx=5, pady=5)

        columns = ("Name", "DOB", "Location", "Priority")  # Added "DOB"
        self.tree = ttk.Treeview(self.patient_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_bay_view(self):
        self.bay_frame = tk.Frame(self.root, bd=1, relief="solid", width=250)
        self.bay_frame.pack(side="left", fill="both", padx=5, pady=5)

        bay_label = tk.Label(self.bay_frame, text="Bay View", font=("Arial", 12, "bold"))
        bay_label.pack(anchor="w", padx=5, pady=5)

        self.beds_frame = tk.Frame(self.bay_frame, bg="lightgray")
        self.beds_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # ---------------- Core Methods ---------------- #
    def refresh_tree(self, bay_filter=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        bays_to_show = [bay_filter] if bay_filter else self.bay_beds.keys()

        for bay_num in bays_to_show:
            for patient in self.bay_beds[bay_num]:
                if patient.presence:
                    patient_name = f"{patient.first_name} {patient.last_name}"
                    patient_dob = patient.dob  # <-- Added
                    patient_location = f"Bay {patient.bay} / Bed {patient.bed}"
                    self.tree.insert("", "end", values=(patient_name, patient_dob, patient_location, patient.priority))

    def update_bed_info(self, curr_patient):
        for i, patient in enumerate(self.bay_beds[curr_patient.bay]):
            if patient.bed == curr_patient.bed:
                self.bay_beds[curr_patient.bay][i] = curr_patient
                break

    # ---------------- Add Patient Dialog ---------------- #
    def add_patient_dialog(self, bay, bed):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add Patient to Bay {bay} Bed {bed}")
        dialog.geometry("300x300")
        dialog.grab_set()

        tk.Label(dialog, text="First Name").pack(pady=2)
        first_name_entry = tk.Entry(dialog)
        first_name_entry.pack(pady=2)

        tk.Label(dialog, text="Last Name").pack(pady=2)
        last_name_entry = tk.Entry(dialog)
        last_name_entry.pack(pady=2)

        tk.Label(dialog, text="DOB (YYYY-MM-DD)").pack(pady=2)
        dob_entry = tk.Entry(dialog)
        dob_entry.pack(pady=2)

        tk.Label(dialog, text="Priority").pack(pady=2)
        priority_var = tk.StringVar(dialog)
        priority_var.set("Medium")
        tk.OptionMenu(dialog, priority_var, "High", "Medium", "Low").pack(pady=2)

        def submit():
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            dob = dob_entry.get().strip()
            priority = priority_var.get()

            if not first_name or not last_name or not dob:
                messagebox.showwarning("Missing Info", "Please fill in all fields")
                return

            # Color based on priority
            priority_colors = {"High": "red", "Medium": "orange", "Low": "green"}
            color = priority_colors.get(priority, "deeppink2")

            self.update_bed_info(Patient(
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                bay=bay,
                bed=bed,
                priority=priority,
                color=color,
                presence=True,
                _id=None
            ))

            self.show_bay(self.current_bay)
            self.refresh_tree(self.current_bay)
            dialog.destroy()

        tk.Button(dialog, text="Add Patient", command=submit).pack(pady=5)

    # ---------------- Bed Methods ---------------- #
    def create_bed(self, frame, patient):
        f = tk.Frame(frame, width=70, height=90, bg="white", bd=1, relief="solid")
        f.pack_propagate(False)

        label = tk.Label(f, text=patient.bed, bg="white", font=("Arial", 10))
        label.pack(side="bottom", pady=5)

        icon_lbl = None
        if patient.presence:
            icon_lbl = tk.Label(f, text="👤", fg=patient.color, bg="darkgray", font=("Arial", 25))
            icon_lbl.pack(side="top", pady=5)

        def on_click(event):
            if self.selected_bed:
                self.selected_bed.config(bd=1, relief="solid", highlightthickness=0)
            f.config(bd=3, relief="solid", highlightbackground="red", highlightcolor="red", highlightthickness=3)
            self.selected_bed = f

            curr_patient = next(
                (p for p in self.bay_beds.get(patient.bay, []) if p.bed == patient.bed),
                None
            )

            if curr_patient.presence:
                self.edit_patient_dialog(curr_patient)
            else:
                self.add_patient_dialog(curr_patient.bay, curr_patient.bed)

        f.bind("<Button-1>", on_click)
        label.bind("<Button-1>", on_click)
        if icon_lbl:
            icon_lbl.bind("<Button-1>", on_click)

        return f

    # ---------------- Edit Patient Dialog ---------------- #
    def edit_patient_dialog(self, patient: Patient):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Patient in Bay {patient.bay} Bed {patient.bed}")
        dialog.geometry("300x350")
        dialog.grab_set()

        tk.Label(dialog, text="First Name").pack(pady=2)
        first_name_entry = tk.Entry(dialog)
        first_name_entry.insert(0, patient.first_name)
        first_name_entry.pack(pady=2)

        tk.Label(dialog, text="Last Name").pack(pady=2)
        last_name_entry = tk.Entry(dialog)
        last_name_entry.insert(0, patient.last_name)
        last_name_entry.pack(pady=2)

        tk.Label(dialog, text="DOB (YYYY-MM-DD)").pack(pady=2)
        dob_entry = tk.Entry(dialog)
        dob_entry.insert(0, patient.dob)
        dob_entry.pack(pady=2)

        tk.Label(dialog, text="Priority").pack(pady=2)
        priority_var = tk.StringVar(dialog)
        priority_var.set(patient.priority)
        tk.OptionMenu(dialog, priority_var, "High", "Medium", "Low").pack(pady=2)

        def save_changes():
            patient.first_name = first_name_entry.get().strip()
            patient.last_name = last_name_entry.get().strip()
            patient.dob = dob_entry.get().strip()
            patient.priority = priority_var.get()
            # Update color based on priority
            priority_colors = {"High": "red", "Medium": "orange", "Low": "green"}
            patient.color = priority_colors.get(patient.priority, "deeppink2")

            self.update_bed_info(patient)
            self.show_bay(self.current_bay)
            self.refresh_tree(self.current_bay)
            dialog.destroy()

        def remove_patient():
            confirm = messagebox.askyesno("Remove Patient",
                                          f"Remove {patient.first_name} {patient.last_name} from Bed {patient.bed}?")
            if confirm:
                self.update_bed_info(Patient.empty(patient.bay, patient.bed))
                self.show_bay(self.current_bay)
                self.refresh_tree(self.current_bay)
                dialog.destroy()

        tk.Button(dialog, text="Save Changes", command=save_changes, bg="lightblue").pack(pady=5)
        tk.Button(dialog, text="Remove Patient", command=remove_patient, bg="salmon", fg="white").pack(pady=5)

    # ---------------- Bay Methods ---------------- #
    def show_bay(self, bay_number):
        if bay_number is None:
            self.current_bay = 1
        else:
            self.current_bay = bay_number

        if self.selected_bed:
            self.selected_bed.config(bd=1, relief="solid", highlightthickness=0)
            self.selected_bed = None

        # Show bed control buttons
        self.bed_control_frame.pack(side="bottom", fill="x", pady=5)

        for widget in self.beds_frame.winfo_children():
            widget.destroy()

        row, col = 0, 0
        for patient in self.bay_beds[self.current_bay]:
            bed = self.create_bed(self.beds_frame, patient)
            bed.grid(row=row, column=col, padx=15, pady=15)
            col += 1
            if col > 2:
                col = 0
                row += 1

        bay_label_under = tk.Label(self.beds_frame, text=f"Bay {bay_number}", font=("Arial", 10, "bold"), bg="lightgray")
        bay_label_under.grid(row=row+1, column=0, columnspan=3, pady=(0,10))

        self.refresh_tree(bay_number)

    def show_all_bays(self):
        self.current_bay = None
        if self.selected_bed:
            self.selected_bed.config(bd=1, relief="solid", highlightthickness=0)
            self.selected_bed = None

        # Hide Add/Remove Bed buttons
        self.bed_control_frame.pack_forget()

        for widget in self.beds_frame.winfo_children():
            widget.destroy()

        bays_per_row = 3
        sorted_bays = sorted(self.bay_beds.items())
        for idx, (bay_num, beds) in enumerate(sorted_bays):
            row = (idx // bays_per_row) * 2
            col = idx % bays_per_row

            bay_container = tk.Frame(self.beds_frame, bd=1, relief="solid", padx=5, pady=5)
            bay_container.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            patients = self.bay_beds.get(bay_num, [])
            for j, patient in enumerate(patients):
                bed_row, bed_col = divmod(j, 3)
                bed = self.create_bed(bay_container, patient)
                bed.grid(row=bed_row, column=bed_col, padx=5, pady=5)

            bay_label_under = tk.Label(self.beds_frame, text=f"Bay {bay_num}", font=("Arial", 10, "bold"), bg="lightgray")
            bay_label_under.grid(row=row+1, column=col, pady=(0,5))

            self.beds_frame.columnconfigure(col, weight=1)
        for r in range(((len(sorted_bays) + bays_per_row - 1) // bays_per_row) * 2):
            self.beds_frame.rowconfigure(r, weight=1)

        self.refresh_tree(None)

    def add_bay(self):
        total_bays = len(self.bay_beds)
        if total_bays >= MAX_BAYS:
            messagebox.showwarning("Limit Reached", f"Maximum of {MAX_BAYS} bays reached!")
            return

        bay_num = total_bays + 1
        self.bay_beds[bay_num] = []

        new_btn = tk.Button(self.bay_buttons_frame, text=f"- Bay {bay_num}", bg="lightgray", relief="flat",
                            command=lambda num=bay_num: self.show_bay(num))
        new_btn.pack(anchor="w", padx=5)

        messagebox.showinfo("Success", f"Bay {bay_num} added successfully!")
        if self.current_bay is None:
            self.show_all_bays()

    def remove_bay(self):
        if len(self.bay_beds) <= 1:
            messagebox.showwarning("Cannot Remove", "There must be at least 1 bay!")
            return

        last_bay = max(self.bay_beds.keys())
        confirm = messagebox.askyesno("Remove Bay", f"Remove Bay {last_bay}?")
        if confirm:
            del self.bay_beds[last_bay]

            # Remove button
            for btn in self.bay_buttons_frame.winfo_children():
                if btn.cget("text") == f"- Bay {last_bay}":
                    btn.destroy()

            # Show last remaining bay
            if self.bay_beds:
                self.show_bay(max(self.bay_beds.keys()))

    def add_bed(self):
        if self.current_bay is None:
            messagebox.showwarning("No Bay Selected", "Please select a specific bay to add a bed.")
            return

        beds_in_bay = self.bay_beds[self.current_bay]
        if len(beds_in_bay) >= MAX_BEDS_PER_BAY:
            messagebox.showwarning("Limit Reached", f"Bay {self.current_bay} can only have {MAX_BEDS_PER_BAY} beds.")
            return

        new_bed_name = f"{len(beds_in_bay)+1}"
        beds_in_bay.append(Patient.empty(self.current_bay, new_bed_name))
        self.show_bay(self.current_bay)

    def remove_bed(self):
        if self.current_bay is None:
            messagebox.showwarning("No Bay Selected", "Select a bay first!")
            return

        beds_in_bay = self.bay_beds[self.current_bay]
        if len(beds_in_bay) <= 1:
            messagebox.showwarning("Cannot Remove", "Each bay must have at least 1 bed!")
            return

        bed_to_remove = beds_in_bay[-1]
        confirm = messagebox.askyesno("Remove Bed", f"Remove {bed_to_remove} from Bay {self.current_bay}?")
        if confirm:
            beds_in_bay.pop()
            self.show_bay(self.current_bay)

    # ---------------- Run ---------------- #
    def run(self):
        self.root.mainloop()


import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

MAX_BAYS = 6
MAX_BEDS_PER_BAY = 6

class BedBuddy:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hospital Dashboard")
        self.root.geometry("1500x450")

        # ---------------- Data ---------------- #
        self.bay_beds = {
            1: [
                ("B1", "yellow", True, "John Green"),
                ("B2", "yellow", True, "Brandon Sanderson"),
                ("B3", "white", False, None)
            ],
            2: [
                ("B1", "yellow", True, "Rick Riordan"),
                ("B2", "white", False, None)
            ]
        }

        # ---------------- State ---------------- #
        self.selected_bed = None
        self.current_bay = 1

        # ---------------- UI Setup ---------------- #
        self.setup_sidebar()
        self.setup_patient_view()
        self.setup_bay_view()
        self.show_bay(1)

    # ---------------- Setup Methods ---------------- #
    def setup_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg="lightgray", width=150)
        self.sidebar.pack(side="left", fill="y")

        # ED Space Label
        myed_label = tk.Label(self.sidebar, text="ED Space", bg="lightgray", font=("Arial", 10, "bold"))
        myed_label.pack(anchor="w", padx=10, pady=(10, 0))

        # Bay Buttons Frame
        self.bay_buttons_frame = tk.Frame(self.sidebar, bg="lightgray")
        self.bay_buttons_frame.pack(anchor="w", padx=10, pady=10, fill="x")

        # Default Bay Buttons
        for i in range(1, len(self.bay_beds)+1):
            btn = tk.Button(self.bay_buttons_frame, text=f"- Bay {i}", bg="lightgray", relief="flat",
                            command=lambda num=i: self.show_bay(num))
            btn.pack(anchor="w", padx=5)

        # Show All Patients Button
        self.patients_btn = tk.Button(self.sidebar, text="Show All Patients", relief="flat", bg="gray25", fg="white",
                                      command=self.show_all_bays)
        self.patients_btn.pack(anchor="w", padx=5, pady=5, fill="x")

        # Add/Remove Bay Control Frame
        self.bay_control_frame = tk.Frame(self.sidebar, bd=1, relief="groove", bg="lightgray", padx=5, pady=5)
        self.bay_control_frame.pack(side="bottom", fill="x", pady=5)

        self.add_bay_btn = tk.Button(self.bay_control_frame, text="+ Add Bay", bg="lightblue", relief="raised",
                                     command=self.add_bay)
        self.remove_bay_btn = tk.Button(self.bay_control_frame, text="- Remove Bottom Bay", bg="red", fg="white",
                                        relief="raised", command=self.remove_bay)

        self.add_bay_btn.pack(fill="x", pady=(0,5))
        self.remove_bay_btn.pack(fill="x", pady=(5,0))

        # Bed Control Frame (for Add/Remove Bed in specific bay)
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

        columns = ("Name", "Location", "Patient Info")
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
            for bedname, color, has_patient, pname in self.bay_beds[bay_num]:
                if has_patient:
                    location = f"Bay {bay_num} / {bedname}"
                    self.tree.insert("", "end", values=(pname, location, "..."))

    def update_bed_info(self, bay_number, bedname, color, has_patient, pname):
        for i, (bname, _, _, _) in enumerate(self.bay_beds[bay_number]):
            if bname == bedname:
                self.bay_beds[bay_number][i] = (bname, color, has_patient, pname)
                break

    def create_bed(self, frame, bed_info, bay_number):
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
            if self.selected_bed:
                self.selected_bed.config(bd=1, relief="solid", highlightthickness=0)
            f.config(bd=3, relief="solid", highlightbackground="red", highlightcolor="red", highlightthickness=3)
            self.selected_bed = f

            _, curr_color, curr_has_patient, curr_name = next(b for b in self.bay_beds[bay_number] if b[0] == bedname)

            if curr_has_patient:
                remove = messagebox.askyesno("Remove Patient", f"Remove {curr_name} from {bedname}?")
                if remove:
                    self.update_bed_info(bay_number, bedname, "white", False, None)
                    self.show_bay(self.current_bay)
                    self.refresh_tree(self.current_bay)
            else:
                pname_input = simpledialog.askstring("Add Patient", f"Enter patient name for {bedname}:")
                if pname_input:
                    self.update_bed_info(bay_number, bedname, "yellow", True, pname_input)
                    self.show_bay(self.current_bay)
                    self.refresh_tree(self.current_bay)

        f.bind("<Button-1>", on_click)
        label.bind("<Button-1>", on_click)
        if icon_lbl:
            icon_lbl.bind("<Button-1>", on_click)

        return f

    # ---------------- Bay Methods ---------------- #
    def show_bay(self, bay_number):
        self.current_bay = bay_number
        if self.selected_bed:
            self.selected_bed.config(bd=1, relief="solid", highlightthickness=0)
            self.selected_bed = None

        # Show bed control buttons
        self.bed_control_frame.pack(side="bottom", fill="x", pady=5)

        for widget in self.beds_frame.winfo_children():
            widget.destroy()

        row, col = 0, 0
        for bed_info in self.bay_beds[bay_number]:
            bed = self.create_bed(self.beds_frame, bed_info, bay_number)
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

            for j, bed_info in enumerate(beds):
                bed_row, bed_col = divmod(j, 3)
                bed = self.create_bed(bay_container, bed_info, bay_num)
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
        self.bay_beds[bay_num] = [(f"B{i+1}", "white", False, None) for i in range(3)]

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

        new_bed_name = f"B{len(beds_in_bay)+1}"
        beds_in_bay.append((new_bed_name, "white", False, None))
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
        confirm = messagebox.askyesno("Remove Bed", f"Remove {bed_to_remove[0]} from Bay {self.current_bay}?")
        if confirm:
            beds_in_bay.pop()
            self.show_bay(self.current_bay)

    # ---------------- Run ---------------- #
    def run(self):
        self.root.mainloop()

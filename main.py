# Entry point
from ui import BedBuddy
from database.db_operation import get_all_patients

patients = get_all_patients()
for patient in patients:
    print(f"Name: {patient['first_name']} {patient['last_name']}")
    print(f"\tLocation: {patient['bed']}")
    print(f"\tDOB: {patient['dob']}")
    print(f"\tPriority: {patient['priority']}")

if __name__ == "__main__":
    app = BedBuddy()
    app.run()
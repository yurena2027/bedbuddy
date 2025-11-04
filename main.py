# Entry point for the BedBuddy application

# This module initalizes the system by: 
#   1. Retrieves patient records from the MongoDB Atalas database

from ui import BedBuddy
from database.db_operation import get_all_patients
#   2. Displays basic patient info
#   3. Launches the BedBuddy graphical interface
#--------------
# Design Notes:
#--------------
# - This script acts as the "controller" connecting the database (model) and UI (view),
#   which follows the MVC (Model–View–Controller) design principle.
# - Using separate modules for database operations and the UI improves maintainability
#   and supports Agile/iterative development practices.
# -----------
# References:
# -----------
# - Python Software Foundation. (2024). The Python Tutorial: Modules and Packages*. 
#  https://docs.python.org/3/tutorial/modules.html
# - MongoDB, Inc. (2025). PyMongo – Python driver for MongoDB. 
# https://pymongo.readthedocs.io/
# - Python Software Foundation. (2024). tkinter — Python interface to Tcl/Tk. 
#  https://docs.python.org/3/library/tkinter.html
# - Reenskaug, T. (1979). Model-View-Controller (MVC) architecture pattern.
#   Xerox PARC technical note.
# - Sommerville, I. (2016). Software Engineering (10th ed.). Pearson Education.
# ====================================================================================

from ui import BedBuddy
from database.db_operation import get_all_patients

# Database retrival
patients = get_all_patients()

# Loop through each patient recrod and rpint key details
for patient in patients:
    print(f"Name: {patient['first_name']} {patient['last_name']}")
    print(f"\tLocation: {patient['bed']}")
    print(f"\tDOB: {patient['dob']}")
    print(f"\tPriority: {patient['priority']}")

if __name__ == "__main__":
    app = BedBuddy()
    app.run()




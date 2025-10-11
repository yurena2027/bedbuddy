# Using PyMongo
from config.db_config import get_db

db = get_db()

# List NAMES of collections (bays), returns LIST[STR]
def get_bays():
    return db.list_collection_names() # Return list of collection names

# List ALL patients in ALL bays, returns LIST[STR]
def get_all_patients():
    bays = get_bays() # Get all bay names
    all_patients: list[str] = [] # New list[str] for all patients
    for bay in bays:
        bay_collection = db[bay] # Get collection of bay name
        all_patients += list(bay_collection.find({ # Append all patients in bay to current list
            "first_name": {"$exists": True, "$ne": ""},
            "last_name": {"$exists": True, "$ne": ""}
        }))
    return all_patients

# PLACEHOLDER for inserting a patient
def insert_patient(patient_data):
    bay_collection = db[patient_data.bay]
    return bay_collection.insert_one(patient_data)

# PLACEHOLDER for deleting a patient
def delete_patient(patient_data):
    bay_collection = db[patient_data.bay]
    return bay_collection.delete_one({"_id": patient_data.patient_id})

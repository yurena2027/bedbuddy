# Using PyMongo
from bson import ObjectId
from database.patient import Patient

class Database:
    def __init__(self, db):
        self.db = db

    # Inserts patient to Mongo - sends it to the same collection as BAY field
    def insert_patient(self, patient: Patient) -> ObjectId:
        collection = self.db[str(patient.bay)]
        result = collection.insert_one(patient.to_dict())
        patient.id = result.inserted_id  # update the patient instance
        return patient.id

    # Deletes patient from Mongo - from same collection as BAY field
    def delete_patient(self, patient: Patient) -> bool:
        if not patient.id:
            raise ValueError("Patient does not have an _id.")
        collection = self.db[str(patient.bay)]
        result = collection.delete_one({"_id": patient.id})
        return result.deleted_count == 1

    # Updates patient in Mongo - same collection as BAY field
    def update_patient(self, patient: Patient) -> bool:
        if not patient.id:
            raise ValueError("Patient does not have an _id.")
        collection = self.db[str(patient.bay)]
        result = collection.update_one(
            {"_id": patient.id},
            {"$set": patient.to_dict()} # all new fields
        )
        return result.modified_count == 1

    # List patients in ONE bay (specified by passed int)
    def get_bay_patients(self, bay: int) -> list[Patient]:
        bay_collection = self.db[str(bay)] # Get bay collection
        docs = bay_collection.find({
            "presence": {"$exists": True, "$eq": True}
        })
        return [Patient.from_document(doc) for doc in docs]

    # List ALL patients
    def get_all_patients(self) -> list[Patient]:
        all_patients = []
        for bay in [int(b) for b in self.db.list_collection_names()]:
            all_patients.extend(self.get_bay_patients(bay))
        return all_patients

from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def fetch_case_database() -> list:
    case_database = []
    try:
        records = list(collection.find({}, {"_id": 0}))

        for record in records:
            case_id = record.get("case_id")
            embedding = record.get("embedding")
            
            if not case_id or embedding is None or not isinstance(embedding, list):
                continue

            case_data = {
                "case_id": str(case_id),
                "embedding": embedding,
                "case_description": record.get("case_description", ""),
                "category": record.get("category"),
                "location": record.get("location"),
                "resolution_notes": record.get("resolution_notes", "")
            }
            case_database.append(case_data)

    except Exception as e:
        print(f"❌ MongoDB Error: {e}")

    return case_database

def insert_case(case_data: dict):
    try:
        if "case_id" not in case_data or "embedding" not in case_data:
            raise ValueError("case_id and embedding are required")
        collection.insert_one(case_data)
    except Exception as e:
        print(f"❌ MongoDB Insert Error: {e}")
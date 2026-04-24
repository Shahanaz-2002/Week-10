from pymongo import MongoClient
import logging
import json
import time

from config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME

logger = logging.getLogger(__name__)


# ---------------- LOG HELPER ----------------
def log_event(event_type, message, extra=None):
    log_data = {
        "event": event_type,
        "message": message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if extra:
        log_data.update(extra)

    logger.info(json.dumps(log_data))


# ---------------- DB CONNECTION ----------------
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Test connection
    client.server_info()

    log_event("db_connected", "MongoDB connection established")

except Exception as e:
    log_event("db_connection_error", "Failed to connect to MongoDB", {
        "error": str(e)
    })
    collection = None


# ---------------- FETCH DATABASE ----------------
def fetch_case_database() -> list:
    case_database = []

    if collection is None:
        log_event("db_unavailable", "MongoDB collection not available")
        return case_database

    try:
        records = list(collection.find({}, {"_id": 0}))

        for record in records:
            try:
                case_id = record.get("case_id")
                embedding = record.get("embedding")

                # Validate required fields
                if not case_id or embedding is None or not isinstance(embedding, list):
                    log_event("invalid_record_skipped", "Skipping invalid record")
                    continue

                case_data = {
                    "case_id": str(case_id),
                    "embedding": embedding,
                    "case_description": record.get("case_description", ""),
                    "category": record.get("category", "Unknown"),
                    "location": record.get("location", "Unknown"),
                    "resolution_notes": record.get("resolution_notes", "")
                }

                case_database.append(case_data)

            except Exception as e:
                log_event("record_processing_error", "Error processing record", {
                    "error": str(e)
                })
                continue

        log_event("db_fetch_success", "Case database loaded", {
            "total_records": len(case_database)
        })

    except Exception as e:
        log_event("db_fetch_error", "Error fetching data from MongoDB", {
            "error": str(e)
        })

    return case_database


# ---------------- INSERT CASE ----------------
def insert_case(case_data: dict):
    if collection is None:
        log_event("db_unavailable", "Insert failed - DB not available")
        return False

    try:
        # Validate required fields
        if not isinstance(case_data, dict):
            raise ValueError("case_data must be a dictionary")

        if "case_id" not in case_data or "embedding" not in case_data:
            raise ValueError("case_id and embedding are required")

        collection.insert_one(case_data)

        log_event("db_insert_success", "Case inserted successfully", {
            "case_id": case_data.get("case_id")
        })

        return True

    except Exception as e:
        log_event("db_insert_error", "Error inserting case", {
            "error": str(e)
        })
        return False
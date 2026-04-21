# utils.py

import pandas as pd
import logging
from typing import Dict, Any

# Configure utility logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# DATA MIGRATION LOADER (CSV to Dictionary format for DB Insertion)
def load_cases_from_csv(file_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Utility function to load historical CCMS cases from a CSV file 
    so they can be passed to embedding_store.py and inserted into MongoDB.
    """
    try:
        df = pd.read_csv(file_path)
        case_database: Dict[str, Dict[str, Any]] = {}

        for _, row in df.iterrows():
            case_id = str(row["case_id"]).strip()

            case_database[case_id] = {
                "case_id": case_id,  
                "case_description": str(row.get("case_description", "")).strip(),
                "category": str(row.get("category", "")).strip(),
                "location": str(row.get("location", "")).strip(),
                "resolution_notes": str(row.get("resolution_notes", "")).strip(),
                "status": str(row.get("status", "Closed")).strip(),
                "resolution_days": row.get("resolution_days", 0),
            }

        logger.info(f"Successfully loaded {len(case_database)} CCMS cases from {file_path}")
        return case_database

    except Exception as e:
        logger.error(f"Failed to load CSV file at {file_path}: {e}")
        return {}
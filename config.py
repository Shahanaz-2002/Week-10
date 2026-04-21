# config.py

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "ccms_ai"
COLLECTION_NAME = "dermatology_cases"

# Retrieval Configuration
TOP_K = 3
EMBEDDING_DIM = 768  # Updated to match BioClinicalBERT output dimensions
EMBEDDING_VERSION = "v1"  # Required for embedding_store.py tracking

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# Confidence Levels (for reference)
VERY_HIGH_CONFIDENCE = 0.85
HIGH_CONFIDENCE = 0.70
MEDIUM_CONFIDENCE = 0.50
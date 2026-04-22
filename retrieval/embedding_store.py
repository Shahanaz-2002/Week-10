import logging
from datetime import datetime

from retrieval.database import collection
from retrieval.embedding import BioBERTEmbedding
from config import EMBEDDING_VERSION

logger = logging.getLogger(__name__)

embedder = BioBERTEmbedding()


def generate_and_store_embeddings():
    records = collection.find({})
    total = collection.count_documents({})
    processed = 0
    skipped = 0
    errors = 0

    logger.info(f"Starting embedding generation for {total} records")

    for record in records:
        try:
            case_id = record.get("case_id")

            # Skip if already embedded
            if record.get("embedding_version") == EMBEDDING_VERSION:
                skipped += 1
                continue

            # ✅ FIXED TEXT EXTRACTION
            text_parts = [
                str(record.get("symptoms", "")),
                str(record.get("diagnosis", "")),
                str(record.get("doctor_notes", ""))
            ]

            text = " ".join([t.strip() for t in text_parts if t]).strip()

            if not text:
                print(f"Empty text for case_id: {case_id}, skipping...")
                skipped += 1
                continue

            # Generate embedding
            embedding = embedder.get_embedding(text)

            # Store in DB
            collection.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "embedding": embedding.tolist(),
                        "embedding_version": EMBEDDING_VERSION,
                        "embedding_created_at": datetime.utcnow()
                    }
                }
            )

            print(f"Embedding stored for {case_id}")
            processed += 1

        except Exception as e:
            print(f"Error for case_id {record.get('case_id')}: {str(e)}")
            errors += 1
            continue

    print("\nDONE")
    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")


if __name__ == "__main__":
    generate_and_store_embeddings()
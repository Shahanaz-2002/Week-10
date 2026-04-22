import logging
from datetime import datetime

from retrieval.database import collection
from retrieval.embedding import BioBERTEmbedding
from config import EMBEDDING_VERSION

logger = logging.getLogger(__name__)

embedder = BioBERTEmbedding()


def generate_and_store_embeddings():
    """
    Generate embeddings for all records and store them in MongoDB
    """

    records = collection.find({})
    total = collection.count_documents({})
    processed = 0
    skipped = 0
    errors = 0

    logger.info(f" Starting embedding generation for {total} records")

    for record in records:
        try:
            case_id = record.get("case_id")

            # 🔹 Skip if embedding already exists with same version
            if record.get("embedding_version") == EMBEDDING_VERSION:
                skipped += 1
                continue

            # 🔹 Get text
            text = str(record.get("case_description", "")).strip()

            if not text:
                logger.warning(f" Empty text for case_id: {case_id}, skipping...")
                skipped += 1
                continue

            # 🔹 Generate embedding
            embedding = embedder.get_embedding(text)

            # 🔹 Store in DB
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

            processed += 1

            # 🔹 Print progress every 10 records
            if processed % 10 == 0:
                logger.info(f" Processed {processed}/{total}")

        except Exception as e:
            logger.error(f" Error processing case_id {record.get('case_id')}: {str(e)}")
            errors += 1
            continue

    logger.info(" Embedding generation completed")
    logger.info(f" Processed: {processed}")
    logger.info(f" Skipped: {skipped}")
    logger.info(f" Errors: {errors}")


if __name__ == "__main__":
    generate_and_store_embeddings()
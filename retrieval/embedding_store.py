from retrieval.database import collection
from retrieval.embedding import BioBERTEmbedding
from config import EMBEDDING_VERSION
from datetime import datetime

embedder = BioBERTEmbedding()

def generate_and_store_embeddings():
    records = collection.find({})

    for record in records:
        case_id = record["case_id"]
        
        # Updated to use the CCMS case description instead of medical fields
        text = str(record.get("case_description", "")).strip()
        
        # Note: If you want the category or location to influence the similarity, 
        # you could append them here, e.g.: text = f"{text} {record.get('category', '')}"

        embedding = embedder.get_embedding(text)

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

if __name__ == "__main__":
    generate_and_store_embeddings()
from typing import List, Dict
import numpy as np
import logging
import json
import time
from retrieval.embedding import BioBERTEmbedding

logger = logging.getLogger(__name__)

embedder = BioBERTEmbedding()


# STRUCTURED LOG HELPER
def log_event(event_type, message, extra=None):
    log_data = {
        "event": event_type,
        "message": message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if extra:
        log_data.update(extra)

    logger.info(json.dumps(log_data))


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    try:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))

    except Exception as e:
        log_event("cosine_error", "Error in cosine similarity", {"error": str(e)})
        return 0.0


def retrieve_similar_cases(query_text: str, case_database: List[Dict], top_k: int = 3) -> List[Dict]:


    start_time = time.time()

    log_event("retrieval_started", "Starting similarity retrieval", {
        "query_length": len(query_text) if query_text else 0,
        "database_size": len(case_database) if isinstance(case_database, list) else 0,
        "top_k": top_k
    })

    
    # INPUT VALIDATION
    
    if not query_text or not isinstance(query_text, str) or not query_text.strip():
        log_event("validation_error", "Invalid query_text received")
        raise ValueError("Query text must be a non-empty string")

    if not isinstance(case_database, list):
        log_event("validation_error", "Invalid case database format")
        raise ValueError("Case database must be a list")

    if not isinstance(top_k, int) or top_k <= 0:
        log_event("top_k_warning", "Invalid top_k value, defaulting to 3")
        top_k = 3

    
    # EMBEDDING GENERATION
    
    try:
        embed_start = time.time()

        query_embedding = embedder.get_embedding(query_text)

        if query_embedding is None or len(query_embedding) == 0:
            log_event("embedding_failure", "Failed to generate query embedding")
            raise ValueError("Embedding generation failed")

        query_embedding = np.array(query_embedding)

        embed_time = round((time.time() - embed_start) * 1000, 2)

        log_event("embedding_generated", "Query embedding created", {
            "embedding_dim": len(query_embedding),
            "embedding_time_ms": embed_time
        })

    except Exception as e:
        log_event("embedding_error", "Error generating embedding", {"error": str(e)})
        raise ValueError("Error generating embedding")

    results = []
    processed_cases = 0

    
    # SIMILARITY COMPUTATION
    
    for case_data in case_database:

        if not isinstance(case_data, dict):
            log_event("invalid_case_skipped", "Skipping invalid case entry")
            continue

        try:
            case_embedding = np.array(case_data.get("embedding", []))

            if case_embedding.size == 0:
                continue

            similarity = cosine_similarity(query_embedding, case_embedding)

            results.append({
                "case_id": case_data.get("case_id", "Unknown"),
                "similarity": similarity,
                "diagnosis": case_data.get("diagnosis", "Unknown"),
                "treatment": case_data.get("treatment", "Unknown"),
                "symptoms": case_data.get("symptoms", [])
            })

            processed_cases += 1

        except Exception as e:
            log_event("case_processing_error", "Skipping case due to error", {
                "error": str(e)
            })
            continue

    log_event("similarity_computed", "Similarity computation completed", {
        "processed_cases": processed_cases,
        "total_results": len(results)
    })

   
    # SORTING & TOP-K SELECTION
    
    try:
        results = sorted(results, key=lambda x: x["similarity"], reverse=True)

        top_results = results[:top_k]

        # Log top-k summary (not full data to avoid heavy logs)
        log_event("top_k_selected", "Top K cases selected", {
            "top_k": top_k,
            "top_case_ids": [r["case_id"] for r in top_results],
            "top_scores": [round(r["similarity"], 4) for r in top_results]
        })

    except Exception as e:
        log_event("sorting_error", "Error during sorting", {"error": str(e)})
        return []

    total_time = round((time.time() - start_time) * 1000, 2)

    log_event("retrieval_finished", "Retrieval pipeline completed", {
        "total_time_ms": total_time
    })

    return top_results
from config import TOP_K
import logging
import json
import time

logger = logging.getLogger(__name__)


# ---------------- LOG FUNCTION ----------------
def log_event(event_type, message, extra=None):
    log_data = {
        "event": event_type,
        "message": message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if extra:
        log_data.update(extra)

    logger.info(json.dumps(log_data))


class ConfidenceEngine:

    def compute_confidence(self, retrieved_cases: list) -> dict:

        start_time = time.time()

        log_event("confidence_start", "Starting confidence computation", {
            "num_cases": len(retrieved_cases) if isinstance(retrieved_cases, list) else 0
        })

        try:
            # ---------------- INPUT VALIDATION ----------------
            if not isinstance(retrieved_cases, list):
                log_event("validation_warning", "retrieved_cases is not a list")
                return {"confidence_score": 0.0}

            if not retrieved_cases:
                log_event("no_cases", "No cases provided for confidence calculation")
                return {"confidence_score": 0.0}

            # ---------------- EXTRACT SIMILARITIES ----------------
            similarities = []

            for case in retrieved_cases:
                try:
                    sim = float(case.get("similarity", 0.0))

                    # Only consider valid similarity values
                    if sim > 0:
                        similarities.append(sim)

                except Exception:
                    log_event("similarity_error", "Invalid similarity value skipped")
                    continue

            # ---------------- SAFETY CHECK ----------------
            if not similarities:
                log_event("no_valid_similarity", "No valid similarity scores found")
                return {"confidence_score": 0.0}

            # ---------------- COMPUTATION ----------------
            avg_similarity = sum(similarities) / len(similarities)

            support_ratio = (
                len(retrieved_cases) / TOP_K if isinstance(TOP_K, int) and TOP_K > 0 else 0
            )

            confidence_score = (0.75 * avg_similarity) + (0.25 * support_ratio)

            # Clamp to [0,1]
            confidence_score = max(0.0, min(1.0, confidence_score))

            total_time = round((time.time() - start_time) * 1000, 2)

            log_event("confidence_computed", "Confidence score calculated", {
                "avg_similarity": round(avg_similarity, 4),
                "support_ratio": round(support_ratio, 4),
                "final_score": round(confidence_score, 4),
                "execution_time_ms": total_time
            })

            return {
                "confidence_score": round(confidence_score, 3)
            }

        # ---------------- ERROR HANDLING ----------------
        except Exception as e:
            log_event("confidence_error", "Error in confidence computation", {
                "error": str(e)
            })

            return {
                "confidence_score": 0.0
            }
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


class ExplanationGenerator:

    def generate_explanation(self, retrieved_cases: list) -> str:

        start_time = time.time()

        log_event("explanation_start", "Generating explanation", {
            "num_cases": len(retrieved_cases) if isinstance(retrieved_cases, list) else 0
        })

        try:
            # ---------------- INPUT VALIDATION ----------------
            if not isinstance(retrieved_cases, list):
                log_event("validation_warning", "retrieved_cases is not a list")
                return "Explanation could not be generated due to invalid input."

            # ---------------- NO CASES ----------------
            if not retrieved_cases:
                log_event("no_cases", "No retrieved cases for explanation")

                return (
                    "No similar cases were found.\n"
                    "Reason: Insufficient historical data.\n"
                    "Recommendation: Proceed with manual review."
                )

            case_count = len(retrieved_cases)

            # ---------------- EXTRACT SIMILARITIES ----------------
            similarities = []

            for case in retrieved_cases:
                try:
                    sim = float(case.get("similarity", 0.0))
                    if sim > 0:
                        similarities.append(sim)
                except Exception:
                    log_event("similarity_error", "Invalid similarity skipped")
                    continue

            # ---------------- AVERAGE SIMILARITY ----------------
            avg_similarity = (sum(similarities) / len(similarities)) * 100 if similarities else 0.0

            # ---------------- TOP CASE ----------------
            top_case = retrieved_cases[0]

            category = top_case.get("category", "Unknown")
            resolution = top_case.get("resolution_notes", "No standard resolution available")

            try:
                top_score = float(top_case.get("similarity", 0.0)) * 100
            except Exception:
                top_score = 0.0

            # ---------------- STRUCTURED EXPLANATION ----------------
            explanation = (
                f"Summary of Analysis:\n"
                f"- Retrieved {case_count} similar case(s) from historical data.\n"
                f"- Top match similarity: {top_score:.1f}%\n"
                f"- Average similarity: {avg_similarity:.1f}%\n\n"
                f"Key Insight:\n"
                f"- Most relevant category: {category}\n"
                f"- Common resolution approach: {resolution}\n\n"
                f"Conclusion:\n"
                f"- The recommendation is based on consistent patterns observed in similar past cases."
            )

            total_time = round((time.time() - start_time) * 1000, 2)

            log_event("explanation_generated", "Explanation created successfully", {
                "execution_time_ms": total_time
            })

            return explanation

        # ---------------- ERROR HANDLING ----------------
        except Exception as e:
            log_event("explanation_error", "Error generating explanation", {
                "error": str(e)
            })

            return "Explanation could not be generated due to an internal error."
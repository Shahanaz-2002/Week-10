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
                    "No similar cases were found in the database. "
                    "The recommendation is based on limited available information."
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
            if not similarities:
                avg_similarity = 0.0
            else:
                avg_similarity = (sum(similarities) / len(similarities)) * 100

            # ---------------- TOP CASE ----------------
            top_case = retrieved_cases[0] if retrieved_cases else {}

            category = top_case.get("category", "an unspecified category")
            resolution = top_case.get("resolution_notes", "standard resolution procedures")

            try:
                top_score = float(top_case.get("similarity", 0.0)) * 100
            except Exception:
                top_score = 0.0

            # ---------------- BUILD EXPLANATION ----------------
            explanation = (
                f"{case_count} similar cases were retrieved from historical data. "
                f"The most relevant case has a similarity score of {top_score:.1f}%, "
                f"falling under category '{category}'. "
                f"On average, retrieved cases show {avg_similarity:.1f}% similarity. "
                f"These cases were commonly resolved by '{resolution}', "
                f"which supports the suggested resolution."
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
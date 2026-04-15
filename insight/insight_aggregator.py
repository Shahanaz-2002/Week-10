from typing import List, Dict
import logging
import json
import time

logger = logging.getLogger(__name__)


# 🔹 LOG FUNCTION
def log_event(event_type, message, extra=None):
    log_data = {
        "event": event_type,
        "message": message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if extra:
        log_data.update(extra)

    logger.info(json.dumps(log_data))


class InsightAggregator:

    def aggregate_insights(
        self,
        top_matches: List[Dict],
        explanation: str,
        confidence_data: Dict
    ) -> Dict:

        start_time = time.time()

        log_event("insight_start", "Starting insight aggregation", {
            "num_cases": len(top_matches) if isinstance(top_matches, list) else 0
        })

        # 🔹 INPUT VALIDATION
        if not isinstance(top_matches, list):
            log_event("validation_error", "top_matches is not a list")
            raise ValueError("top_matches must be a list")

        if not top_matches:
            log_event("no_matches", "No matches provided to aggregator")

            return {
                "suggested_resolution": "No similar cases found. Unable to suggest a resolution.",
                "confidence_score": confidence_data.get("confidence_score", 0.0),
                "explanation": explanation or "No explanation available."
            }

        diagnosis_score = {}
        treatment_score = {}
        processed_cases = 0

        # 🔹 PROCESS EACH CASE
        for case in top_matches:

            if not isinstance(case, dict):
                log_event("invalid_case", "Skipping non-dict case")
                continue

            try:
                diagnosis = case.get("diagnosis")
                treatment = case.get("treatment")

                
                similarity = float(case.get("similarity", 0.0))

                # 🔹 Skip invalid similarity
                if similarity <= 0:
                    continue

                # 🔹 Aggregate diagnosis
                if diagnosis and isinstance(diagnosis, str) and diagnosis.strip():
                    diagnosis_clean = diagnosis.strip()
                    diagnosis_score[diagnosis_clean] = (
                        diagnosis_score.get(diagnosis_clean, 0.0) + similarity
                    )

                # 🔹 Aggregate treatment
                if treatment and isinstance(treatment, str) and treatment.strip():
                    treatment_clean = treatment.strip()
                    treatment_score[treatment_clean] = (
                        treatment_score.get(treatment_clean, 0.0) + similarity
                    )

                processed_cases += 1

            except Exception as e:
                log_event("case_processing_error", "Skipping malformed case", {
                    "error": str(e)
                })
                continue

        log_event("aggregation_done", "Scores aggregated", {
            "processed_cases": processed_cases,
            "unique_diagnosis": len(diagnosis_score),
            "unique_treatments": len(treatment_score)
        })

        # 🔹 FINAL PREDICTION
        predicted_diagnosis = (
            max(diagnosis_score, key=diagnosis_score.get)
            if diagnosis_score else "Unknown condition"
        )

        predicted_treatment = (
            max(treatment_score, key=treatment_score.get)
            if treatment_score else "No treatment pattern found"
        )

        log_event("prediction_generated", "Final prediction created", {
            "diagnosis": predicted_diagnosis,
            "treatment": predicted_treatment
        })

        # 🔹 FINAL RESOLUTION STRING
        suggested_resolution = (
            f"Based on similar cases, the likely diagnosis is '{predicted_diagnosis}' "
            f"and the recommended treatment is '{predicted_treatment}'."
        )

        total_time = round((time.time() - start_time) * 1000, 2)

        log_event("insight_completed", "Insight aggregation completed", {
            "execution_time_ms": total_time
        })

        # 🔹 FINAL RESPONSE
        return {
            "suggested_resolution": suggested_resolution,
            "confidence_score": confidence_data.get("confidence_score", 0.0),
            "explanation": explanation or "No explanation available."
        }
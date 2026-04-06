from typing import List, Dict
import logging
import json
import time

logger = logging.getLogger(__name__)



#  LOG 

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

    def aggregate_insights(self, top_matches: List[Dict]) -> Dict:

        start_time = time.time()

        log_event("insight_start", "Starting insight aggregation", {
            "num_cases": len(top_matches) if isinstance(top_matches, list) else 0
        })

        
        # INPUT VALIDATION
        
        if not isinstance(top_matches, list):
            log_event("validation_error", "top_matches is not a list")
            raise ValueError("top_matches must be a list")

        if not top_matches:
            log_event("no_matches", "No matches provided to aggregator")

            return {
                "diagnosis": "Unknown condition",
                "treatment": "No treatment pattern available"
            }

        diagnosis_score = {}
        treatment_score = {}
        processed_cases = 0

        
        # PROCESS EACH CASE
        
        for case in top_matches:

            if not isinstance(case, dict):
                log_event("invalid_case", "Skipping non-dict case")
                continue

            try:
                diagnosis = case.get("diagnosis")
                treatment = case.get("treatment")
                similarity = float(case.get("similarity", 0.0))

                # Skip invalid similarity
                if similarity < 0:
                    log_event("invalid_similarity", "Negative similarity skipped", {
                        "value": similarity
                    })
                    continue

                # Aggregate diagnosis scores
                if diagnosis and isinstance(diagnosis, str) and diagnosis.strip():
                    diagnosis_clean = diagnosis.strip()
                    diagnosis_score[diagnosis_clean] = (
                        diagnosis_score.get(diagnosis_clean, 0.0) + similarity
                    )

                # Aggregate treatment scores
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

        
        # FINAL PREDICTION
        
        if diagnosis_score:
            predicted_diagnosis = max(diagnosis_score, key=diagnosis_score.get)
        else:
            predicted_diagnosis = "Unknown condition"

        if treatment_score:
            predicted_treatment = max(treatment_score, key=treatment_score.get)
        else:
            predicted_treatment = "No treatment pattern found"

        log_event("prediction_generated", "Final prediction created", {
            "diagnosis": predicted_diagnosis,
            "treatment": predicted_treatment
        })

        total_time = round((time.time() - start_time) * 1000, 2)

        log_event("insight_completed", "Insight aggregation completed", {
            "execution_time_ms": total_time
        })

        return {
            "diagnosis": predicted_diagnosis,
            "treatment": predicted_treatment
        }
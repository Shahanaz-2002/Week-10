import time
import logging
import uuid
import json
from fastapi import FastAPI, HTTPException
import uvicorn

from models.models import CaseRequest, CaseResponse, SimilarCase, SystemMetrics
from retrieval.retrieval_engine import retrieve_similar_cases
from retrieval.database import fetch_case_database
from insight.insight_aggregator import InsightAggregator
from insight.confidence_engine import ConfidenceEngine
from insight.explanation_generator import ExplanationGenerator
from config import TOP_K


# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    force=True
)
logger = logging.getLogger(__name__)

def log_event(event_type, request_id, message, extra=None):
    log_data = {
        "event": event_type,
        "request_id": request_id,
        "message": message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if extra:
        log_data.update(extra)
    logger.info(json.dumps(log_data))


app = FastAPI(title="Clinical Insight Engine API", version="1.0")

# 🔹 Initialize Engines & Cache DB
logger.info("Initializing Insight Engines and loading Case Database...")

try:
    case_database = fetch_case_database()
    if not case_database:
        logger.warning("Case database is empty or failed to load!")
        case_database = []
    else:
        logger.info(f"Successfully loaded {len(case_database)} cases into memory.")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    case_database = []

insight_aggregator = InsightAggregator()
confidence_engine = ConfidenceEngine()
explanation_generator = ExplanationGenerator()


@app.post("/analyze-case", response_model=CaseResponse)
def analyze_case(request: CaseRequest):

    request_id = str(uuid.uuid4())  # 🔹 Unique request tracking
    start_time = time.time()

    log_event("request_received", request_id, "Incoming request", {
        "symptom_count": len(request.symptoms) if request.symptoms else 0,
        "age": request.age,
        "gender": request.gender
    })

    
    # INPUT VALIDATION
    
    if not request.symptoms or not isinstance(request.symptoms, list) or len(request.symptoms) == 0:
        raise HTTPException(status_code=400, detail="Symptoms must be a non-empty list")

    if any(not s or not s.strip() for s in request.symptoms):
        raise HTTPException(status_code=400, detail="Symptoms list contains empty values")

    if request.age < 0 or request.age > 120:
        raise HTTPException(status_code=400, detail="Invalid age")

    if request.gender.lower() not in ["male", "female", "other"]:
        raise HTTPException(status_code=400, detail="Invalid gender")

    try:
        # INPUT FORMATTING
        doctor_notes = request.doctor_notes.strip() if request.doctor_notes else ""
        query_text = " ".join(request.symptoms).strip()

        if doctor_notes:
            query_text += " " + doctor_notes

        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is empty")

        log_event("input_processed", request_id, "Input formatted successfully")

        
        # RETRIEVAL
       
        retrieval_start = time.time()

        log_event("retrieval_started", request_id, f"Fetching top {TOP_K} cases")

        top_matches = retrieve_similar_cases(
            query_text=query_text,
            case_database=case_database,
            top_k=TOP_K
        )

        retrieval_time = round((time.time() - retrieval_start) * 1000, 2)

        log_event("retrieval_completed", request_id, "Cases retrieved", {
            "num_cases": len(top_matches) if top_matches else 0,
            "retrieval_time_ms": retrieval_time
        })

        if not top_matches:
            response_time = round((time.time() - start_time) * 1000, 2)

            log_event("no_cases_found", request_id, "No similar cases found")

            return CaseResponse(
                status="success",
                similar_cases=[],
                predicted_diagnosis="No matching cases found",
                suggested_treatment="Not available",
                confidence_score=0.0,
                confidence_level="Low",
                clinical_explanation="No similar clinical patterns were found in the database.",
                system_metrics=SystemMetrics(
                    response_time_ms=response_time,
                    output_quality="Poor - No Matches"
                )
            )

        
        # INSIGHT GENERATION
        
        insight_start = time.time()

        insight = insight_aggregator.aggregate_insights(top_matches)

        if not insight:
            raise ValueError("Insight aggregation failed")

        log_event("insight_generated", request_id, "Insight created", {
            "diagnosis": insight.get("diagnosis")
        })

        
        # CONFIDENCE
        
        confidence_data = confidence_engine.compute_confidence(top_matches)

        log_event("confidence_computed", request_id, "Confidence calculated", {
            "score": confidence_data.get("confidence_score")
        })

        
        # EXPLANATION
        
        explanation = explanation_generator.generate_explanation(insight, top_matches)

        log_event("explanation_generated", request_id, "Explanation created")

        
        # FORMAT SIMILAR CASES
        
        similar_cases_formatted = []

        for c in top_matches:
            try:
                similar_cases_formatted.append(
                    SimilarCase(
                        case_id=c.get("case_id", "Unknown"),
                        similarity_score=float(c.get("similarity", 0.0)),
                        diagnosis=c.get("diagnosis", "Unknown"),
                        treatment=c.get("treatment", "Unknown")
                    )
                )
            except Exception as e:
                log_event("case_format_warning", request_id, "Malformed case skipped", {
                    "error": str(e)
                })

        response_time = round((time.time() - start_time) * 1000, 2)

        log_event("response_ready", request_id, "Response prepared", {
            "response_time_ms": response_time
        })

        return CaseResponse(
            status="success",
            similar_cases=similar_cases_formatted,
            predicted_diagnosis=insight.get("diagnosis", "Unknown"),
            suggested_treatment=insight.get("treatment", "Not specified"),
            confidence_score=confidence_data.get("confidence_score", 0.0),
            confidence_level=confidence_data.get("confidence_level", "Unknown"),
            clinical_explanation=explanation,
            system_metrics=SystemMetrics(
                response_time_ms=response_time,
                output_quality="High" if confidence_data.get("confidence_score", 0) > 0.7 else "Moderate"
            )
        )

    except HTTPException:
        raise

    except Exception as e:
        log_event("pipeline_error", request_id, "Pipeline failure", {
            "error": str(e)
        })

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal Server Error"
            }
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
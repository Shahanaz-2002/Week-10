import time
import logging
from fastapi import FastAPI, HTTPException
import uvicorn

from models.models import CaseRequest, CaseResponse, SimilarCase, SystemMetrics
from retrieval.retrieval_engine import retrieve_similar_cases
from retrieval.database import fetch_case_database
from insight.insight_aggregator import InsightAggregator
from insight.confidence_engine import ConfidenceEngine
from insight.explanation_generator import ExplanationGenerator
from config import TOP_K

# 🔹 Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
    force=True
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Clinical Insight Engine API", version="1.0")

# 🔹 Initialize Engines & Cache DB
logger.info("Initializing Insight Engines and loading Case Database...")
try:
    case_database = fetch_case_database()
    if not case_database:
        logger.warning("Case database is empty or failed to load!")
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
    start_time = time.time()

    # 🔴 Input Validation (Day 1 requirement)
    if not request.symptoms or len(request.symptoms) == 0:
        raise HTTPException(status_code=400, detail="Symptoms are required")

    logger.info(f"Received new case analysis request. Symptoms count: {len(request.symptoms)}")

    try:
        # 🔹 1. Format Input
        logger.info("Formatting input text for embedding generation...")
        doctor_notes = request.doctor_notes if request.doctor_notes else ""
        query_text = " ".join(request.symptoms) + " " + doctor_notes

        # 🔹 2. Retrieve Similar Cases
        logger.info(f"Querying retrieval engine for top {TOP_K} matches...")
        top_matches = retrieve_similar_cases(
            query_text=query_text,
            case_database=case_database,
            top_k=TOP_K
        )

        if not top_matches:
            logger.warning("No similar cases retrieved. Returning default response.")

            response_time = round((time.time() - start_time) * 1000, 2)

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

        logger.info(f"Successfully retrieved {len(top_matches)} similar cases.")

        # 🔹 3. Generate Insights
        logger.info("Aggregating clinical insights from retrieved cases...")
        insight = insight_aggregator.aggregate_insights(top_matches)

        # 🔹 4. Compute Confidence
        logger.info("Computing confidence score...")
        confidence_data = confidence_engine.compute_confidence(top_matches)

        # 🔹 5. Generate Explanation
        logger.info("Generating clinical explanation...")
        explanation = explanation_generator.generate_explanation(insight, top_matches)

        # 🔹 6. Format Similar Cases
        similar_cases_formatted = [
            SimilarCase(
                case_id=c["case_id"],
                similarity_score=c["similarity"],
                diagnosis=c.get("diagnosis", "Unknown"),
                treatment=c.get("treatment", "Unknown")
            ) for c in top_matches
        ]

        response_time = round((time.time() - start_time) * 1000, 2)

        logger.info(f"Request processed successfully in {response_time}ms")

        # 🔹 7. Final Response (API Contract Standard)
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

    except Exception as e:
        logger.error(f"Error during case analysis pipeline: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal Server Error processing case"
            }
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
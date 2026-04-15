import time
from fastapi import HTTPException

from models.models import SimilarCase
from retrieval.retrieval_engine import retrieve_similar_cases
from retrieval.database import fetch_case_database
from insight.insight_aggregator import InsightAggregator
from insight.confidence_engine import ConfidenceEngine
from insight.explanation_generator import ExplanationGenerator
from config import TOP_K


# Initialize once
case_database = fetch_case_database()

insight_aggregator = InsightAggregator()
confidence_engine = ConfidenceEngine()
explanation_generator = ExplanationGenerator()


def analyze_case_pipeline(request, request_id, log_event=None):
    start_time = time.time()

    try:
        # 🔹 INPUT FORMATTING
        doctor_notes = request.doctor_notes.strip() if request.doctor_notes else ""
        query_text = " ".join(request.symptoms).strip()

        if doctor_notes:
            query_text += " " + doctor_notes

        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is empty")

        if log_event:
            log_event("input_processed", request_id, "Input formatted successfully")

        # 🔹 RETRIEVAL
        top_matches = retrieve_similar_cases(
            query_text=query_text,
            case_database=case_database,
            top_k=TOP_K
        )

        if log_event:
            log_event("retrieval_completed", request_id, "Cases retrieved", {
                "num_cases": len(top_matches) if top_matches else 0
            })

        # 🔹 FORMAT SIMILAR CASES 
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
            except Exception:
                continue

        # 🔹 NO MATCH CASE
        if not similar_cases_formatted:
            return {
                "suggested_resolution": "No similar cases found. Unable to provide a recommendation.",
                "similar_cases": [],
                "confidence_score": 0.0,
                "explanation": "No similar clinical patterns were found in the database."
            }

        # 🔹 CONFIDENCE
        confidence_data = confidence_engine.compute_confidence(top_matches)

        # 🔹 EXPLANATION
        explanation = explanation_generator.generate_explanation(top_matches)

        # 🔹 FINAL INSIGHT
        final_insight = insight_aggregator.aggregate_insights(
            top_matches=top_matches,
            explanation=explanation,
            confidence_data=confidence_data
        )

        # 🔹 FINAL RESPONSE
        return {
            "suggested_resolution": final_insight.get("suggested_resolution"),
            "similar_cases": similar_cases_formatted,
            "confidence_score": final_insight.get("confidence_score"),
            "explanation": final_insight.get("explanation")
        }

    except HTTPException:
        raise

    except Exception as e:
        if log_event:
            log_event("pipeline_error", request_id, "Pipeline failure", {
                "error": str(e)
            })

        raise HTTPException(
            status_code=500,
            detail={
                "suggested_resolution": "Error occurred while processing the request",
                "similar_cases": [],
                "confidence_score": 0.0,
                "explanation": str(e)
            }
        )
import time
from fastapi import HTTPException

from models.models import SimilarCase
from retrieval.retrieval_engine import retrieve_similar_cases
from retrieval.database import fetch_case_database
from insight.insight_aggregator import InsightAggregator
from insight.confidence_engine import ConfidenceEngine
from insight.explanation_generator import ExplanationGenerator
from config import TOP_K


# ---------------- INITIALIZE COMPONENTS ----------------
try:
    case_database = fetch_case_database()
except Exception:
    case_database = []

insight_aggregator = InsightAggregator()
confidence_engine = ConfidenceEngine()
explanation_generator = ExplanationGenerator()


# ---------------- MAIN PIPELINE ----------------
def analyze_case_pipeline(request, request_id, log_event=None):
    start_time = time.time()

    try:
        # ---------------- INPUT FORMATTING ----------------
        query_text = (request.case_description or "").strip()

        if not query_text:
            raise HTTPException(
                status_code=400,
                detail="case_description is empty"
            )

        if log_event:
            log_event("input_processed", request_id, "Input formatted successfully")

        # ---------------- RETRIEVAL ----------------
        try:
            top_matches = retrieve_similar_cases(
                query_text=query_text,
                case_database=case_database,
                top_k=TOP_K
            )
        except Exception as e:
            if log_event:
                log_event("retrieval_error", request_id, "Retrieval failed", {
                    "error": str(e)
                })
            raise HTTPException(
                status_code=500,
                detail="Error during similarity retrieval"
            )

        # ---------------- NO MATCH CASE ----------------
        if not top_matches:
            if log_event:
                log_event("no_matches", request_id, "No similar cases found")

            return {
                "suggested_resolution": (
                    "No similar cases were found.\n"
                    "Recommended Action: Escalate for manual review."
                ),
                "similar_cases": [],
                "confidence_score": 0.0,
                "explanation": (
                    "No similar cases were found.\n"
                    "Reason: Insufficient historical data.\n"
                    "Recommendation: Proceed with manual analysis."
                )
            }

        if log_event:
            log_event("retrieval_completed", request_id, "Cases retrieved", {
                "num_cases": len(top_matches)
            })

        # ---------------- FORMAT SIMILAR CASES ----------------
        similar_cases_formatted = []

        for c in top_matches:
            try:
                similar_cases_formatted.append(
                    SimilarCase(
                        case_id=str(c.get("case_id", "Unknown")),
                        similarity_score=max(0.0, min(1.0, float(c.get("similarity", 0.0)))),
                        category=c.get("category", "Unknown") or "Unknown",
                        location=c.get("location", "Unknown") or "Unknown",
                        resolution_notes=c.get("resolution_notes", "No resolution available") or "No resolution available"
                    )
                )
            except Exception:
                continue

        # If formatting fails completely
        if not similar_cases_formatted:
            if log_event:
                log_event("formatting_issue", request_id, "All retrieved cases invalid")

            return {
                "suggested_resolution": (
                    "Relevant cases found but could not be processed.\n"
                    "Recommended Action: Verify data integrity."
                ),
                "similar_cases": [],
                "confidence_score": 0.0,
                "explanation": "Retrieved data was not in expected format."
            }

        # ---------------- CONFIDENCE ----------------
        try:
            confidence_data = confidence_engine.compute_confidence(top_matches)
        except Exception as e:
            if log_event:
                log_event("confidence_error", request_id, "Confidence calculation failed", {
                    "error": str(e)
                })
            confidence_data = {"confidence_score": 0.0}

        # ---------------- EXPLANATION ----------------
        try:
            explanation = explanation_generator.generate_explanation(top_matches)
        except Exception as e:
            if log_event:
                log_event("explanation_error", request_id, "Explanation generation failed", {
                    "error": str(e)
                })
            explanation = "Explanation could not be generated."

        # ---------------- FINAL INSIGHT ----------------
        try:
            final_insight = insight_aggregator.aggregate_insights(
                top_matches=top_matches,
                explanation=explanation,
                confidence_data=confidence_data
            )
        except Exception as e:
            if log_event:
                log_event("aggregation_error", request_id, "Insight aggregation failed", {
                    "error": str(e)
                })
            raise HTTPException(
                status_code=500,
                detail="Error during insight aggregation"
            )

        total_time = round((time.time() - start_time) * 1000, 2)

        if log_event:
            log_event("pipeline_completed", request_id, "Pipeline executed successfully", {
                "total_time_ms": total_time
            })

        # ---------------- FINAL RESPONSE ----------------
        return {
            "suggested_resolution": final_insight.get(
                "suggested_resolution",
                "No suggestion available"
            ),
            "similar_cases": similar_cases_formatted,
            "confidence_score": float(final_insight.get("confidence_score", 0.0)),
            "explanation": final_insight.get("explanation", explanation)
        }

    # ---------------- EXPECTED ERRORS ----------------
    except HTTPException:
        raise

    # ---------------- UNEXPECTED ERRORS ----------------
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
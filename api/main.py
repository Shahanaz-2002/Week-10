import time
import logging
import uuid
import json
from fastapi import FastAPI, HTTPException, Request
import uvicorn

from models.models import CaseRequest, CaseResponse
from services.analyze_service import analyze_case_pipeline


# ---------------- LOGGING CONFIG ----------------
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


# ---------------- FASTAPI APP ----------------
app = FastAPI(
    title="Case Insight Engine API",
    version="1.0"
)


# ---------------- API ROUTE ----------------
@app.post("/ai/analyze-case", response_model=CaseResponse)
def analyze_case(request: CaseRequest):

    request_id = str(uuid.uuid4())
    start_time = time.time()

    # ---------------- INPUT VALIDATION ----------------
    if not request.case_description or not request.case_description.strip():
        log_event("validation_error", request_id, "Empty case description")

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid Input",
                "message": "case_description cannot be empty"
            }
        )

    # Optional: validate length
    if len(request.case_description.strip()) < 10:
        log_event("validation_error", request_id, "Too short input")

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid Input",
                "message": "case_description too short for analysis"
            }
        )

    # ---------------- REQUEST LOG ----------------
    log_event("request_received", request_id, "Incoming request", {
        "input_length": len(request.case_description)
    })

    try:
        # ---------------- SERVICE CALL ----------------
        result = analyze_case_pipeline(request, request_id)

        # ---------------- EMPTY RESULT HANDLING ----------------
        if not result:
            log_event("no_result", request_id, "No result returned from pipeline")

            raise HTTPException(
                status_code=404,
                detail={
                    "error": "No Results",
                    "message": "No similar cases found",
                    "suggested_resolution": "Manual review required",
                    "similar_cases": [],
                    "confidence_score": 0.0
                }
            )

        # ---------------- RESPONSE TIME ----------------
        response_time = round((time.time() - start_time) * 1000, 2)

        log_event("response_ready", request_id, "Response prepared", {
            "response_time_ms": response_time
        })

        return CaseResponse(**result)

    # ---------------- EXPECTED ERRORS ----------------
    except HTTPException as http_err:
        log_event("http_error", request_id, "Handled HTTP exception", {
            "status_code": http_err.status_code,
            "detail": http_err.detail
        })
        raise http_err

    # ---------------- UNEXPECTED ERRORS ----------------
    except Exception as e:
        log_event("pipeline_error", request_id, "Pipeline failure", {
            "error": str(e)
        })

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Error occurred while processing the request",
                "suggested_resolution": "Please try again later",
                "similar_cases": [],
                "confidence_score": 0.0,
                "explanation": str(e)
            }
        )



@app.get("/health")
def health_check():
    return {"status": "API is running"}


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
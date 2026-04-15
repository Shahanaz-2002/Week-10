import time
import logging
import uuid
import json
from fastapi import FastAPI, HTTPException
import uvicorn

from models.models import CaseRequest, CaseResponse
from services.analyze_service import analyze_case_pipeline  


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


@app.post("/analyze-case", response_model=CaseResponse)
def analyze_case(request: CaseRequest):

    request_id = str(uuid.uuid4())
    start_time = time.time()

    log_event("request_received", request_id, "Incoming request", {
        "symptom_count": len(request.symptoms) if request.symptoms else 0,
        "age": request.age,
        "gender": request.gender
    })

    try:
        # 🔹 Call service layer
        result = analyze_case_pipeline(request, request_id)

        response_time = round((time.time() - start_time) * 1000, 2)

        log_event("response_ready", request_id, "Response prepared", {
            "response_time_ms": response_time
        })

        
        return CaseResponse(**result)

    except HTTPException:
        raise

    except Exception as e:
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
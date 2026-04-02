from pydantic import BaseModel, Field
from typing import List, Optional

# 🔹 REQUEST MODEL
class CaseRequest(BaseModel):
    patient_id: str = Field(..., description="Unique patient identifier")
    symptoms: List[str] = Field(..., min_items=1, description="List of patient symptoms")
    doctor_notes: Optional[str] = Field(None, description="Clinical notes from the doctor")
    age: int = Field(..., ge=0, le=120, description="Patient age")
    gender: str = Field(..., description="Patient gender")


# 🔹 SIMILAR CASE MODEL
class SimilarCase(BaseModel):
    case_id: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    diagnosis: str
    treatment: str


# 🔹 SYSTEM METRICS MODEL
class SystemMetrics(BaseModel):
    response_time_ms: float = Field(..., ge=0)
    output_quality: str = Field(..., min_length=1)


# 🔹 FINAL RESPONSE MODEL
class CaseResponse(BaseModel):
    status: str = Field(..., description="success or error")
    similar_cases: List[SimilarCase]
    predicted_diagnosis: str = Field(default="Unknown")
    suggested_treatment: str = Field(default="No treatment available")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_level: str = Field(default="Low Confidence")
    clinical_explanation: str = Field(default="No explanation available")
    system_metrics: SystemMetrics
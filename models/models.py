from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


# 🔹 REQUEST MODEL
class CaseRequest(BaseModel):
    patient_id: str = Field(
        ...,
        min_length=1,
        description="Unique patient identifier"
    )

    symptoms: List[str] = Field(
        ...,
        min_items=1,
        description="List of patient symptoms"
    )

    doctor_notes: Optional[str] = Field(
        default="",
        description="Clinical notes from the doctor"
    )

    age: int = Field(
        ...,
        ge=0,
        le=120,
        description="Patient age"
    )

    gender: str = Field(
        ...,
        description="Patient gender (male/female/other)"
    )

    # 🔹 Validators
    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("patient_id cannot be empty")
        return v

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v):
        cleaned = []
        for s in v:
            if not s or not s.strip():
                raise ValueError("Symptoms list contains empty values")
            cleaned.append(s.strip())
        return cleaned

    @field_validator("doctor_notes")
    @classmethod
    def validate_doctor_notes(cls, v):
        return v.strip() if v else ""

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        v = v.strip().lower()
        if v not in ["male", "female", "other"]:
            raise ValueError("Gender must be 'male', 'female', or 'other'")
        return v


# 🔹 SIMILAR CASE MODEL
class SimilarCase(BaseModel):
    case_id: str = Field(..., min_length=1)

    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score between 0 and 1"
    )

    diagnosis: str = Field(..., min_length=1)
    treatment: str = Field(..., min_length=1)


# 🔹 FINAL STANDARDIZED RESPONSE MODEL (Day 4)
class CaseResponse(BaseModel):
    suggested_resolution: str = Field(
        ...,
        description="Final suggested resolution based on similar cases"
    )

    similar_cases: List[SimilarCase] = Field(
        default_factory=list,
        description="List of retrieved similar cases"
    )

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1"
    )

    explanation: str = Field(
        ...,
        description="Explanation of how the result was derived"
    )
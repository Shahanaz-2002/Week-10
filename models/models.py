from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


# ---------------- REQUEST MODEL ----------------
class CaseRequest(BaseModel):
    customer_id: str = Field(
        ...,
        min_length=1,
        description="Unique customer identifier"
    )

    case_description: str = Field(
        ...,
        min_length=10,
        description="Detailed description of the case"
    )

    location: Optional[str] = Field(
        default="",
        description="Location associated with the case"
    )

    category: Optional[str] = Field(
        default="",
        description="Optional pre-defined category"
    )

    # ---------------- VALIDATORS ----------------
    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("customer_id cannot be empty")
        return v

    @field_validator("case_description")
    @classmethod
    def validate_case_description(cls, v):
        v = v.strip()
        if len(v) < 10:
            raise ValueError("case_description must be at least 10 characters long")
        return v

    @field_validator("location", "category", mode="before")
    @classmethod
    def clean_optional_fields(cls, v):
        if v is None:
            return ""
        return v.strip()


# ---------------- SIMILAR CASE MODEL ----------------
class SimilarCase(BaseModel):
    case_id: str = Field(..., min_length=1)

    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score between 0 and 1"
    )

    category: str = Field(
        default="Unknown",
        description="Category of the similar case"
    )

    location: str = Field(
        default="Unknown",
        description="Location associated with the case"
    )

    resolution_notes: str = Field(
        default="No resolution provided",
        description="How the case was resolved"
    )


# ---------------- FINAL RESPONSE MODEL ----------------
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
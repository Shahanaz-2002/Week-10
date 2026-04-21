from pydantic import BaseModel, Field, field_validator
from typing import List

class CaseRequest(BaseModel):
    case_description: str = Field(
        ...,
        min_length=5,
        description="Detailed description of the case"
    )

    # Validator
    @field_validator("case_description")
    @classmethod
    def validate_case_description(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("case_description cannot be empty")
        return v

# SIMILAR CASE MODEL 
class SimilarCase(BaseModel):
    case_id: str = Field(..., min_length=1)

    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score between 0 and 1"
    )

    category: str = Field(..., min_length=1, description="Category of the similar case")
    location: str = Field(..., description="Location associated with the case")
    resolution_notes: str = Field(..., min_length=1, description="How the case was resolved")

# FINAL STANDARDIZED RESPONSE MODEL 
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
from pydantic import BaseModel, Field, validator
from typing import Optional


class CaseRequest(BaseModel):
    customer_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique customer identifier"
    )

    case_description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Detailed description of the customer's issue or complaint"
    )

    location: Optional[str] = Field(
        None,
        max_length=100,
        description="Location associated with the complaint"
    )

    category: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional pre-assigned category of the complaint"
    )

    # ---------------- VALIDATORS ----------------

    @validator("customer_id")
    def validate_customer_id(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("customer_id cannot be empty")
        return v

    @validator("case_description")
    def validate_case_description(cls, v):
        v = v.strip()

        if not v:
            raise ValueError("case_description cannot be empty")

        if len(v) < 10:
            raise ValueError("case_description must be at least 10 characters long")

        return v

    @validator("location", "category", pre=True, always=True)
    def validate_optional_strings(cls, v):
        if v is None:
            return ""
        v = v.strip()
        return v if v else ""
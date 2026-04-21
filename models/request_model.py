from pydantic import BaseModel, Field, validator
from typing import Optional


class CaseRequest(BaseModel):
    customer_id: str = Field(
        ...,
        min_length=1,
        description="Unique customer identifier"
    )

    case_description: str = Field(
        ...,
        min_length=5,
        description="Detailed description of the customer's issue or complaint"
    )

    location: Optional[str] = Field(
        None,
        description="Location associated with the complaint"
    )

    category: Optional[str] = Field(
        None,
        description="Optional pre-assigned category of the complaint"
    )

    # VALIDATORS

    @validator("customer_id")
    def validate_customer_id(cls, v):
        if not v or not v.strip():
            raise ValueError("customer_id cannot be empty")
        return v.strip()

    @validator("case_description")
    def validate_case_description(cls, v):
        if not v or not v.strip():
            raise ValueError("case_description cannot be empty")
        return v.strip()

    @validator("location", "category", always=True)
    def validate_optional_strings(cls, v):
        if v is None:
            return ""
        return v.strip()
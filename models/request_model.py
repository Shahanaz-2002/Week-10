from pydantic import BaseModel
from typing import List, Optional

class CaseRequest(BaseModel):
    patient_id: str
    symptoms: List[str]
    doctor_notes: Optional[str] = None
    age: int
    gender: str
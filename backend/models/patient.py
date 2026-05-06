from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MedicalCode(BaseModel):
    system: str = Field(..., description="Coding system (e.g., ICD-10-CM, CPT, SNOMED-CT, RxNorm)")
    code: str = Field(..., description="The medical code (e.g., J45.909)")
    description: str = Field(..., description="Text description of the code")

class PatientRecord(BaseModel):
    mrd: str = Field(..., description="Medical Record Number")
    patient_name: str
    dob: str = Field(..., description="Date of Birth (YYYY-MM-DD)")
    gender: str
    diagnoses: List[MedicalCode] = Field(default_factory=list, description="List of diagnosed conditions")
    procedures: List[MedicalCode] = Field(default_factory=list, description="List of medical procedures performed")
    medications: List[MedicalCode] = Field(default_factory=list, description="List of prescribed medications")
    provider_id: Optional[str] = None
    notes: Optional[str] = None

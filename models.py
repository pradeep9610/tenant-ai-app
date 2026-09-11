from pydantic import BaseModel, EmailStr
from typing import Optional

class TenantApplication(BaseModel):
    full_name: str
    email: str
    country: str  # US, UK, or UAE
    annual_income: float
    credit_score: Optional[int] = None
    employment_status: str

class VerificationResponse(BaseModel):
    application_id: str
    status: str
    risk_score: int
    recommendation: str
    
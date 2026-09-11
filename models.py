from pydantic import BaseModel, EmailStr
from typing import Optional

class TenantApplication(BaseModel):
    full_name: str
    email: str
    country: str  # US, UK, or UAE
    annual_income: float
    credit_score: Optional[int] = None
    employment_status: str
    
    # Country-specific fields
    ssn_last4: Optional[str] = None       # US Specific
    emirates_id: Optional[str] = None     # UAE Specific
    right_to_rent_valid: Optional[bool] = None  # UK Specific

class VerificationResponse(BaseModel):
    application_id: str
    country: str
    status: str
    risk_score: int
    recommendation: str
    breakdown: list[str]
from fastapi import FastAPI
from models import TenantApplication, VerificationResponse
import uuid

app = FastAPI(title="Tenant Screening AI API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Tenant Screening AI API"}

@app.post("/verify-tenant", response_model=VerificationResponse)
def verify_tenant(application: TenantApplication):
    # Basic Rule-Based Verification Logic for US/UK/UAE
    risk_score = 20
    recommendation = "Approved"

    if application.annual_income < 30000:
        risk_score += 40
        recommendation = "Manual Review Required"
    
    if application.credit_score and application.credit_score < 600:
        risk_score += 30
        recommendation = "High Risk - Guarantor Required"

    return {
        "application_id": str(uuid.uuid4()),
        "status": "Processed",
        "risk_score": risk_score,
        "recommendation": recommendation
    }
from fastapi import FastAPI, HTTPException
from models import TenantApplication, VerificationResponse
import uuid

app = FastAPI(title="Tenant Screening AI API")

@app.get("/")
def read_root():
    return {"message": "Tenant Screening AI Service Online"}

@app.post("/verify-tenant", response_model=VerificationResponse)
def verify_tenant(application: TenantApplication):
    country = application.country.upper()
    risk_score = 0
    flags = []

    # 1. Income Check (Universal)
    if application.annual_income < 30000:
        risk_score += 35
        flags.append("Income below minimum threshold ($30,000 / £25,000 / AED 110,000).")

    # 2. Country-Specific Validation Rules
    if country == "US":
        if not application.ssn_last4 or len(application.ssn_last4) != 4:
            flags.append("US Compliance Warning: Missing or invalid 4-digit SSN.")
            risk_score += 20
        if application.credit_score and application.credit_score < 620:
            risk_score += 30
            flags.append("US Credit Warning: Credit score below 620 threshold.")

    elif country == "UK":
        if application.right_to_rent_valid is False:
            risk_score += 100
            flags.append("UK Legal Error: Failed Right to Rent immigration check.")
        elif application.right_to_rent_valid is None:
            flags.append("UK Compliance Warning: Right to Rent verification pending.")
            risk_score += 15

    elif country == "UAE":
        if not application.emirates_id:
            risk_score += 40
            flags.append("UAE Compliance Error: Missing Emirates ID.")
        if application.annual_income < 72000:  # ~6,000 AED/month threshold
            risk_score += 25
            flags.append("UAE Market Warning: Income below UAE standard rent-to-income ratio.")

    else:
        raise HTTPException(status_code=400, detail="Unsupported country. Supported markets: US, UK, UAE")

    # Final Decision Output
    if risk_score >= 70:
        recommendation = "Rejected / Guarantor Mandatory"
    elif risk_score >= 30:
        recommendation = "Manual Review Required"
    else:
        recommendation = "Approved"

    return {
        "application_id": str(uuid.uuid4()),
        "country": country,
        "status": "Processed",
        "risk_score": risk_score,
        "recommendation": recommendation,
        "breakdown": flags
    }
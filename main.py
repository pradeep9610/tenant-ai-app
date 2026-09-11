from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
import uuid

import database
import db_models
from models import TenantApplication, VerificationResponse

# Initialize SQLite DB tables on startup
db_models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Tenant Screening AI API")

@app.get("/")
def read_root():
    return {"message": "Tenant Screening AI Service Online"}

# 1. CREATE: Screen & Save Tenant Application
@app.post("/verify-tenant", response_model=VerificationResponse)
def verify_tenant(
    application: TenantApplication, 
    db: Session = Depends(database.get_db)
):
    country = application.country.upper()
    risk_score = 0
    flags = []

    # Income Check
    if application.annual_income < 30000:
        risk_score += 35
        flags.append("Income below minimum threshold ($30,000 / £25,000 / AED 110,000).")

    # Country Rules Check
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
        if application.annual_income < 72000:
            risk_score += 25
            flags.append("UAE Market Warning: Income below UAE standard rent-to-income ratio.")

    else:
        raise HTTPException(status_code=400, detail="Unsupported country. Supported markets: US, UK, UAE")

    # Final Risk Assessment
    if risk_score >= 70:
        recommendation = "Rejected / Guarantor Mandatory"
    elif risk_score >= 30:
        recommendation = "Manual Review Required"
    else:
        recommendation = "Approved"

    app_id = str(uuid.uuid4())

    # Save to SQLite Database
    db_record = db_models.DBTenantApplication(
        id=app_id,
        full_name=application.full_name,
        email=application.email,
        country=country,
        annual_income=application.annual_income,
        credit_score=application.credit_score,
        employment_status=application.employment_status,
        risk_score=risk_score,
        recommendation=recommendation
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "application_id": app_id,
        "country": country,
        "status": "Processed & Saved",
        "risk_score": risk_score,
        "recommendation": recommendation,
        "breakdown": flags
    }

# 2. READ ALL: Fetch all applications
@app.get("/applications")
def get_all_applications(db: Session = Depends(database.get_db)):
    return db.query(db_models.DBTenantApplication).all()

# 3. READ ONE: Fetch single application by ID
@app.get("/applications/{app_id}")
def get_application(app_id: str, db: Session = Depends(database.get_db)):
    application = db.query(db_models.DBTenantApplication).filter(db_models.DBTenantApplication.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

# 4. UPDATE: Change recommendation status (e.g., Manual Override)
@app.put("/applications/{app_id}")
def update_application_status(app_id: str, new_recommendation: str, db: Session = Depends(database.get_db)):
    application = db.query(db_models.DBTenantApplication).filter(db_models.DBTenantApplication.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application.recommendation = new_recommendation
    db.commit()
    db.refresh(application)
    return {"message": "Application status updated successfully", "updated_record": application}

# 5. DELETE: Remove an application record
@app.delete("/applications/{app_id}")
def delete_application(app_id: str, db: Session = Depends(database.get_db)):
    application = db.query(db_models.DBTenantApplication).filter(db_models.DBTenantApplication.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(application)
    db.commit()
    return {"message": f"Application {app_id} deleted successfully"}
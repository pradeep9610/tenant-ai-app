from sqlalchemy import Column, String, Float, Integer, Boolean
from database import Base

class DBTenantApplication(Base):
    __tablename__ = "tenant_applications"

    id = Column(String, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String)
    country = Column(String)
    annual_income = Column(Float)
    credit_score = Column(Integer, nullable=True)
    employment_status = Column(String)
    risk_score = Column(Integer)
    recommendation = Column(String)
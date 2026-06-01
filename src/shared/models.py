# Shared Pydantic schemas used by all agents and the orchestrator
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class BorrowerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    annual_income: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=850)
    employment_status: str  # "employed" | "self_employed" | "unemployed"
    company_name: Optional[str] = None


class BorrowerOut(BorrowerCreate):
    borrower_id: str
    created_at: datetime


class LoanApplicationCreate(BaseModel):
    borrower_id: str
    loan_amount: float = Field(..., gt=0, le=50_000_000)
    loan_term_months: int = Field(..., ge=3, le=360)
    purpose: str              # "working_capital" | "acquisition" | "real_estate" | etc.
    collateral_type: Optional[str] = None
    collateral_value: Optional[float] = None


class LoanApplicationOut(LoanApplicationCreate):
    loan_id: str
    ltv_ratio: Optional[float] = None  # loan-to-value
    debt_service_ratio: Optional[float] = None
    status: str  # "pending" | "approved" | "rejected"
    created_at: datetime


class CreditIntelRequest(BaseModel):
    borrower_id: str
    loan_id: str


class CreditIntelOut(BaseModel):
    borrower_id: str
    loan_id: str
    risk_score: float        # 0-100, higher = riskier
    default_probability: float  # 0-1
    risk_factors: list[str]
    market_insights: str
    recommendation: str      # "APPROVE" | "DECLINE" | "REVIEW"
    generated_at: datetime


class CreditCommitteeSummary(BaseModel):
    borrower: BorrowerOut
    loan: LoanApplicationOut
    intelligence: CreditIntelOut
    final_recommendation: str
    narrative: str
# FastAPI app — Loan Application Agent (port 8002)
import json, logging
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from shared.models import LoanApplicationCreate, LoanApplicationOut
from shared.config import INTERNAL_API_KEY
from .db import init_db, get_db
from .handlers import structure_loan, get_loan

logging.basicConfig(level="INFO")
app = FastAPI(title="Loan Application Agent", version="1.0.0")
AGENT_CARD = json.loads((Path(__file__).parent / "agent_card.json").read_text())


def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/.well-known/agent-card")
async def agent_card():
    return AGENT_CARD


@app.post("/loans", response_model=LoanApplicationOut, dependencies=[Depends(require_api_key)])
async def create_loan(
    data: LoanApplicationCreate,
    annual_income: float = Query(..., gt=0, description="Borrower annual income for DSR calc"),
    db: Session = Depends(get_db),
):
    try:
        return structure_loan(data, annual_income, db)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/loans/{loan_id}", response_model=LoanApplicationOut, dependencies=[Depends(require_api_key)])
async def fetch_loan(loan_id: str, db: Session = Depends(get_db)):
    loan = get_loan(loan_id, db)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan
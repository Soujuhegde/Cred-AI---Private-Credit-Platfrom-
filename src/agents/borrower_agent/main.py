# FastAPI app — Borrower Onboarding Agent (port 8001)
import json, logging
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from shared.models import BorrowerCreate, BorrowerOut
from shared.config import INTERNAL_API_KEY
from .db import init_db, get_db
from .handlers import onboard_borrower, get_borrower

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

app = FastAPI(title="Borrower Onboarding Agent", version="1.0.0")

AGENT_CARD = json.loads(
    (Path(__file__).parent / "agent_card.json").read_text()
)


def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Borrower Agent ready on :8001")


# ── A2A Discovery ──────────────────────────────────────────────────────────────
@app.get("/.well-known/agent-card")
async def agent_card():
    """A2A discovery endpoint — returns agent capabilities."""
    return AGENT_CARD


# ── Business Endpoints ─────────────────────────────────────────────────────────
@app.post("/borrowers", response_model=BorrowerOut, dependencies=[Depends(require_api_key)])
async def create_borrower(data: BorrowerCreate, db: Session = Depends(get_db)):
    try:
        return onboard_borrower(data, db)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/borrowers/{borrower_id}", response_model=BorrowerOut, dependencies=[Depends(require_api_key)])
async def fetch_borrower(borrower_id: str, db: Session = Depends(get_db)):
    borrower = get_borrower(borrower_id, db)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    return borrower
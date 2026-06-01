# FastAPI app — Credit Intelligence Agent (port 8003)
import json, logging
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Header
from shared.models import CreditIntelRequest, CreditIntelOut, BorrowerOut, LoanApplicationOut
from shared.config import INTERNAL_API_KEY
from .handlers import generate_intelligence
from .rag import query_intelligence

from .db import init_db

logging.basicConfig(level="INFO")
app = FastAPI(title="Credit Intelligence Agent", version="1.0.0")
AGENT_CARD = json.loads((Path(__file__).parent / "agent_card.json").read_text())


@app.on_event("startup")
async def startup():
    init_db()


def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/.well-known/agent-card")
async def agent_card():
    return AGENT_CARD


@app.post("/intelligence", response_model=CreditIntelOut, dependencies=[Depends(require_api_key)])
async def create_intelligence(
    req: CreditIntelRequest,
    borrower: BorrowerOut,
    loan: LoanApplicationOut,
):
    """Generate and persist credit intelligence for a borrower+loan pair."""
    try:
        return await generate_intelligence(req, borrower, loan)
    except Exception as e:
        logging.error("Intelligence generation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/intelligence/query", dependencies=[Depends(require_api_key)])
async def rag_query(q: str, n: int = 3):
    """RAG retrieval endpoint — semantic search over stored intelligence."""
    results = query_intelligence(q, n_results=n)
    return {"query": q, "results": results}
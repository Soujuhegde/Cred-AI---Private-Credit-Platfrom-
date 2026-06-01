# FastAPI app — Concierge Agent / Orchestrator (port 8000)
import json, logging
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from shared.models import BorrowerCreate, LoanApplicationCreate, CreditCommitteeSummary
from shared.config import INTERNAL_API_KEY
from .discovery import discover_agents
from .graph import workflow, WorkflowState

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

app = FastAPI(title="Concierge Agent (Orchestrator)", version="1.0.0")
AGENT_CARD = json.loads((Path(__file__).parent / "agent_card.json").read_text())


def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.on_event("startup")
async def startup():
    logger.info("Concierge Agent ready on :8000 — discovering peers...")
    try:
        cards = await discover_agents()
        logger.info("Discovered %d agents: %s", len(cards), list(cards.keys()))
    except Exception as e:
        logger.warning("Some agents unavailable at startup: %s", e)


@app.get("/.well-known/agent-card")
async def agent_card():
    return AGENT_CARD


@app.get("/agents", dependencies=[Depends(require_api_key)])
async def list_agents():
    """List all discovered agent cards."""
    return await discover_agents()


class FullApplicationRequest(BaseModel):
    borrower: BorrowerCreate
    loan: LoanApplicationCreate


@app.post("/process", response_model=CreditCommitteeSummary, dependencies=[Depends(require_api_key)])
async def process_application(req: FullApplicationRequest):
    """
    Full end-to-end loan origination workflow via LangGraph.
    Orchestrates: Borrower → Loan → Credit Intelligence → Report
    """
    logger.info("Starting full workflow for: %s", req.borrower.email)

    initial_state: WorkflowState = {
        "borrower_input": req.borrower,
        "loan_input": req.loan,
        "borrower": None,
        "loan": None,
        "intelligence": None,
        "summary": None,
        "error": None,
    }

    final_state = await workflow.ainvoke(initial_state)

    if final_state.get("error"):
        raise HTTPException(status_code=422, detail=final_state["error"])

    return final_state["summary"]


@app.get("/query", dependencies=[Depends(require_api_key)])
async def rag_query(q: str):
    """
    Proxy RAG query to Credit Intelligence Agent.
    Example: GET /query?q=what is the risk profile of loan LN-XXXX
    """
    from shared.a2a_client import A2AClient
    from shared.config import CREDIT_AGENT_URL
    client = A2AClient(CREDIT_AGENT_URL)
    return await client.get(f"/intelligence/query?q={q}")
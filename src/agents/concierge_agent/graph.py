# LangGraph orchestration — the core workflow state machine
import logging
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from shared.models import (
    BorrowerCreate, LoanApplicationCreate, CreditIntelRequest,
    BorrowerOut, LoanApplicationOut, CreditIntelOut, CreditCommitteeSummary,
)
from shared.a2a_client import A2AClient
from shared.config import BORROWER_AGENT_URL, LOAN_AGENT_URL, CREDIT_AGENT_URL
from openai import OpenAI   # same SDK, different base_url
import os
from shared.config import OPENAI_API_KEY, LLM_MODEL
from .discovery import discover_agents

logger = logging.getLogger(__name__)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

_llm = OpenAI(
    api_key=SARVAM_API_KEY,
    base_url="https://api.sarvam.ai/v1",   # Sarvam's OpenAI-compatible endpoint
)


# ── State Definition ───────────────────────────────────────────────────────────
class WorkflowState(TypedDict):
    # Inputs
    borrower_input: BorrowerCreate
    loan_input: LoanApplicationCreate

    # Intermediate outputs
    borrower: Optional[BorrowerOut]
    loan: Optional[LoanApplicationOut]
    intelligence: Optional[CreditIntelOut]

    # Final
    summary: Optional[CreditCommitteeSummary]
    error: Optional[str]


# ── Node Functions ─────────────────────────────────────────────────────────────
async def node_onboard_borrower(state: WorkflowState) -> dict:
    """Step 1: Call Borrower Agent to onboard the borrower."""
    logger.info("[Graph] Onboarding borrower...")
    client = A2AClient(BORROWER_AGENT_URL)
    try:
        data = await client.post("/borrowers", state["borrower_input"].model_dump())
        return {"borrower": BorrowerOut(**data)}
    except Exception as e:
        return {"error": f"Borrower onboarding failed: {e}"}


async def node_structure_loan(state: WorkflowState) -> dict:
    """Step 2: Call Loan Agent to structure the deal."""
    if state.get("error"):
        return {}
    logger.info("[Graph] Structuring loan for borrower %s...", state["borrower"].borrower_id)
    client = A2AClient(LOAN_AGENT_URL)
    try:
        loan_data = state["loan_input"].model_dump()
        loan_data["borrower_id"] = state["borrower"].borrower_id
        data = await client.post(
            f"/loans?annual_income={state['borrower'].annual_income}",
            loan_data,
        )
        return {"loan": LoanApplicationOut(**data)}
    except Exception as e:
        return {"error": f"Loan structuring failed: {e}"}


async def node_generate_intelligence(state: WorkflowState) -> dict:
    """Step 3: Call Credit Intelligence Agent for risk analysis + RAG ingest."""
    if state.get("error"):
        return {}
    logger.info("[Graph] Generating credit intelligence for loan %s...", state["loan"].loan_id)
    client = A2AClient(CREDIT_AGENT_URL)
    try:
        payload = {
            "req": CreditIntelRequest(
                borrower_id=state["borrower"].borrower_id,
                loan_id=state["loan"].loan_id,
            ).model_dump(mode="json"),
            "borrower": state["borrower"].model_dump(mode="json"),
            "loan": state["loan"].model_dump(mode="json"),
        }
        data = await client.post("/intelligence", payload)
        return {"intelligence": CreditIntelOut(**data)}
    except Exception as e:
        return {"error": f"Credit intelligence failed: {e}"}


async def node_generate_report(state: WorkflowState) -> dict:
    """Step 4: Synthesize Credit Committee Summary using LLM."""
    if state.get("error"):
        return {}
    logger.info("[Graph] Generating credit committee report...")

    intel = state["intelligence"]
    borrower = state["borrower"]
    loan = state["loan"]
    
    clean_purpose = str(loan.purpose).replace("_", " ")
    clean_employment = str(borrower.employment_status).replace("_", " ")
    
    prompt = f"""You are a helpful senior credit committee analyst. Write an encouraging, highly readable 3-paragraph credit memo in plain English based on the following data.
    
IMPORTANT: The borrower and everyday branch employees will read this. You MUST explain any financial acronyms or terms simply so anyone can understand them (for example, explain 'LTV / Loan-to-Value' as 'how much you are borrowing compared to what your collateral property is worth', and 'DSR / Debt Service Ratio' as 'what percentage of your monthly income is needed to pay back this loan'). Keep the tone supportive, professional, and completely free of complex banking jargon.

CRITICAL: Do NOT include literally written label tags, section headers, or prefixes such as "Paragraph 1:", "Paragraph 2:", "Paragraph 3:", or "Credit Memo for...". Simply output the paragraphs directly. This is extremely important to maintain a professional, clean presentation.

CRITICAL: ALWAYS use standard spaces between words. Do NOT generate words separated by underscores (for example, write 'working capital' instead of 'working_capital', and 'self employed' instead of 'self_employed'). Every word in your output must be separated by standard spaces. No snake_case or underscores are allowed anywhere in the generated text!

BORROWER: {borrower.name}, Income ${borrower.annual_income:,.0f}, Credit Score {borrower.credit_score}, Employment: {clean_employment}
LOAN: ${loan.loan_amount:,.0f} for {clean_purpose} over {loan.loan_term_months} months
      LTV: {loan.ltv_ratio or 'N/A'}, DSR: {loan.debt_service_ratio:.1%}
RISK: Score {intel.risk_score}/100, Default Prob {intel.default_probability:.1%}
FACTORS: {', '.join(intel.risk_factors) or 'None identified'}
MARKET: {intel.market_insights}
RECOMMENDATION: {intel.recommendation}

Structure it as follows:
- Paragraph 1: Clear, jargon-free overview of the borrower (Chirag) and their request.
- Paragraph 2: Explanation of the loan terms, risk levels, and simple, friendly definitions of the debt service and collateral ratios.
- Paragraph 3: The decision (Approved, Needs Review, or Declined) explained in warm, supportive, and practical plain-English terms."""

    response = _llm.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )
    raw_narrative = response.choices[0].message.content or ""
    import re
    narrative = re.sub(r"<think>.*?(?:</think>|$)", "", raw_narrative, flags=re.DOTALL).strip()

    summary = CreditCommitteeSummary(
        borrower=borrower,
        loan=loan,
        intelligence=intel,
        final_recommendation=intel.recommendation,
        narrative=narrative,
    )
    return {"summary": summary}


def should_continue(state: WorkflowState) -> str:
    """Route to END if there's an error, otherwise continue."""
    return "end" if state.get("error") else "continue"


# ── Graph Assembly ─────────────────────────────────────────────────────────────
def build_graph() -> StateGraph:
    graph = StateGraph(WorkflowState)

    graph.add_node("onboard_borrower",       node_onboard_borrower)
    graph.add_node("structure_loan",         node_structure_loan)
    graph.add_node("generate_intelligence",  node_generate_intelligence)
    graph.add_node("generate_report",        node_generate_report)

    graph.set_entry_point("onboard_borrower")

    # Each step checks for errors before proceeding
    graph.add_conditional_edges(
        "onboard_borrower",
        should_continue,
        {"continue": "structure_loan", "end": END},
    )
    graph.add_conditional_edges(
        "structure_loan",
        should_continue,
        {"continue": "generate_intelligence", "end": END},
    )
    graph.add_conditional_edges(
        "generate_intelligence",
        should_continue,
        {"continue": "generate_report", "end": END},
    )
    graph.add_edge("generate_report", END)

    return graph.compile()


# Singleton compiled graph
workflow = build_graph()
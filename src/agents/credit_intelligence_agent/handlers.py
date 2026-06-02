# Credit risk scoring + RAG ingestion
import logging
from datetime import datetime, timezone
from openai import OpenAI   # same SDK, different base_url
import os
from shared.models import CreditIntelRequest, CreditIntelOut, BorrowerOut, LoanApplicationOut
from shared.config import OPENAI_API_KEY, LLM_MODEL
from .rag import upsert_intelligence

logger = logging.getLogger(__name__)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

_llm = OpenAI(
    api_key=SARVAM_API_KEY,
    base_url="https://api.sarvam.ai/v1",   # Sarvam's OpenAI-compatible endpoint
)


def _compute_risk_score(borrower: BorrowerOut, loan: LoanApplicationOut) -> tuple[float, float, list[str]]:
    """
    Heuristic risk scoring (replace with ML model in production).
    Returns (risk_score 0-100, default_probability 0-1, risk_factors).
    """
    score = 50.0
    factors = []

    # Credit score factor (300-850 range)
    if borrower.credit_score >= 750:
        score -= 15
    elif borrower.credit_score < 600:
        score += 25
        factors.append("Low credit score (<600)")

    # DSR factor
    if loan.debt_service_ratio and loan.debt_service_ratio > 0.35:
        score += 20
        factors.append(f"High debt-service ratio ({loan.debt_service_ratio:.1%})")

    # LTV factor
    if loan.ltv_ratio and loan.ltv_ratio > 0.65:
        score += 10
        factors.append(f"Elevated LTV ({loan.ltv_ratio:.1%})")

    # Employment factor
    if borrower.employment_status == "unemployed":
        score += 20
        factors.append("Borrower is unemployed")
    elif borrower.employment_status == "self_employed":
        score += 5
        factors.append("Self-employed income variability")

    # Loan purpose factor
    if loan.purpose == "acquisition":
        score += 5
        factors.append("Acquisition loans carry integration risk")

    score = max(0.0, min(100.0, score))
    default_prob = score / 200  # simple mapping 0-0.5

    return round(score, 2), round(default_prob, 4), factors


async def generate_intelligence(
    req: CreditIntelRequest,
    borrower: BorrowerOut,
    loan: LoanApplicationOut,
) -> CreditIntelOut:
    """
    Generate credit intelligence, persist to RAG, return structured output.
    """
    try:
        risk_score, default_prob, risk_factors = _compute_risk_score(borrower, loan)

        # Generate market insights via LLM
        prompt = f"""You are a credit analyst. Provide a concise, easy-to-understand market insight (2-3 sentences) in plain English for:
- Borrower: {borrower.employment_status} at {borrower.company_name or 'N/A'}, credit score {borrower.credit_score}
- Loan: ${loan.loan_amount:,.0f} for {loan.purpose} over {loan.loan_term_months} months
- Risk score: {risk_score}/100, default probability: {default_prob:.1%}
Avoid heavy banking or industrial jargon. Write simply and clearly so any ordinary person or business owner can understand it."""

        response = _llm.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        raw_insights = response.choices[0].message.content or ""
        import re
        market_insights = re.sub(r"<think>.*?(?:</think>|$)", "", raw_insights, flags=re.DOTALL).strip()

        recommendation = (
            "APPROVE" if risk_score < 40
            else "REVIEW" if risk_score < 65
            else "DECLINE"
        )

        intel = CreditIntelOut(
            borrower_id=req.borrower_id,
            loan_id=req.loan_id,
            risk_score=risk_score,
            default_probability=default_prob,
            risk_factors=risk_factors,
            market_insights=market_insights,
            recommendation=recommendation,
            generated_at=datetime.now(timezone.utc),
        )

        # Persist to RAG for future retrieval
        doc_text = (
            f"Borrower {borrower.name} | Loan {loan.loan_id} | "
            f"Risk {risk_score} | Factors: {', '.join(risk_factors)} | "
            f"Insights: {market_insights}"
        )
        upsert_intelligence(
            doc_id=f"{req.borrower_id}_{req.loan_id}",
            text=doc_text,
            metadata={
                "borrower_id": req.borrower_id,
                "loan_id": req.loan_id,
                "risk_score": risk_score,
                "recommendation": recommendation,
            },
        )

        # Persist to SQL DB
        try:
            from .db import SessionLocal, save_intelligence_record
            with SessionLocal() as db:
                save_intelligence_record(
                    db=db,
                    borrower_id=req.borrower_id,
                    loan_id=req.loan_id,
                    risk_score=risk_score,
                    default_probability=default_prob,
                    recommendation=recommendation,
                    risk_factors=risk_factors,
                    market_insights=market_insights,
                    model_used=LLM_MODEL,
                    language_code="en-IN",
                    narrative=""
                )
        except Exception as e:
            logger.error("Failed to save credit intelligence to DB: %s", e)

        logger.info("Generated credit intelligence: %s score=%.1f rec=%s",
                    req.loan_id, risk_score, recommendation)
        return intel

    except Exception as e:
        logger.error("Failed to generate credit intelligence: %s", e)
        try:
            from .db import SessionLocal, log_error_event
            with SessionLocal() as db:
                log_error_event(db, req.borrower_id, req.loan_id, str(e))
        except Exception as db_err:
            logger.error("Failed to log error to DB: %s", db_err)
        raise
import uuid, logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from shared.models import LoanApplicationCreate, LoanApplicationOut
from .db import LoanRecord

logger = logging.getLogger(__name__)

# Private credit constraints
MAX_LTV            = 0.75   # 75% loan-to-value
MAX_DSR            = 0.45   # 45% debt-service ratio
MIN_LOAN_AMOUNT    = 100_000
ANNUAL_RATE_APPROX = 0.10   # approximate 10% for DSR calc


def structure_loan(data: LoanApplicationCreate, annual_income: float, db: Session) -> LoanApplicationOut:
    """
    Structure a loan deal and compute risk ratios.
    Raises ValueError on constraint violations.
    """
    if data.loan_amount < MIN_LOAN_AMOUNT:
        raise ValueError(f"Minimum loan amount is ${MIN_LOAN_AMOUNT:,}")

    # Compute LTV
    ltv_ratio = None
    if data.collateral_value and data.collateral_value > 0:
        ltv_ratio = data.loan_amount / data.collateral_value
        if ltv_ratio > MAX_LTV:
            logger.warning(f"LTV ratio {ltv_ratio:.1%} exceeds maximum {MAX_LTV:.1%}")

    # Compute monthly debt-service ratio
    monthly_payment = (
        data.loan_amount
        * (ANNUAL_RATE_APPROX / 12)
        / (1 - (1 + ANNUAL_RATE_APPROX / 12) ** -data.loan_term_months)
    )
    dsr = (monthly_payment * 12) / annual_income
    if dsr > MAX_DSR:
        logger.warning(f"Debt service ratio {dsr:.1%} exceeds maximum {MAX_DSR:.1%}")

    loan_id = f"LN-{uuid.uuid4().hex[:8].upper()}"
    record = LoanRecord(
        loan_id=loan_id,
        ltv_ratio=round(ltv_ratio, 4) if ltv_ratio else None,
        debt_service_ratio=round(dsr, 4),
        status="pending",
        created_at=datetime.now(timezone.utc),
        **data.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    logger.info("Structured loan %s for borrower %s | DSR=%.2f", loan_id, data.borrower_id, dsr)

    return LoanApplicationOut(
        **data.model_dump(),
        loan_id=loan_id,
        ltv_ratio=record.ltv_ratio,
        debt_service_ratio=record.debt_service_ratio,
        status=record.status,
        created_at=record.created_at,
    )


def get_loan(loan_id: str, db: Session) -> LoanApplicationOut | None:
    r = db.query(LoanRecord).filter_by(loan_id=loan_id).first()
    if not r:
        return None
    return LoanApplicationOut(
        borrower_id=r.borrower_id, loan_amount=r.loan_amount,
        loan_term_months=r.loan_term_months, purpose=r.purpose,
        collateral_type=r.collateral_type, collateral_value=r.collateral_value,
        loan_id=r.loan_id, ltv_ratio=r.ltv_ratio,
        debt_service_ratio=r.debt_service_ratio, status=r.status,
        created_at=r.created_at,
    )
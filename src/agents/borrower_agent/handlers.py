# Business logic for borrower onboarding
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from shared.models import BorrowerCreate, BorrowerOut
from .db import BorrowerRecord

logger = logging.getLogger(__name__)


def onboard_borrower(data: BorrowerCreate, db: Session) -> BorrowerOut:
    """
    Validate and persist a new borrower.
    Raises ValueError for business-rule violations.
    """
    # Business rule: minimum income for private credit
    if data.annual_income < 50_000:
        raise ValueError("Annual income below minimum threshold ($50,000)")

    # Check for duplicate email
    existing = db.query(BorrowerRecord).filter_by(email=data.email).first()
    if existing:
        logger.info("Borrower with email %s already exists. Returning existing profile %s.", data.email, existing.borrower_id)
        return BorrowerOut(
            borrower_id=existing.borrower_id,
            name=existing.name,
            email=existing.email,
            annual_income=existing.annual_income,
            credit_score=existing.credit_score,
            employment_status=existing.employment_status,
            company_name=existing.company_name,
            created_at=existing.created_at,
        )

    borrower_id = f"BRW-{uuid.uuid4().hex[:8].upper()}"
    record = BorrowerRecord(
        borrower_id=borrower_id,
        **data.model_dump(),
        created_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    logger.info("Onboarded borrower %s (%s)", borrower_id, data.email)

    return BorrowerOut(
        **data.model_dump(),
        borrower_id=borrower_id,
        created_at=record.created_at,
    )


def get_borrower(borrower_id: str, db: Session) -> BorrowerOut | None:
    record = db.query(BorrowerRecord).filter_by(borrower_id=borrower_id).first()
    if not record:
        return None
    return BorrowerOut(
        borrower_id=record.borrower_id,
        name=record.name,
        email=record.email,
        annual_income=record.annual_income,
        credit_score=record.credit_score,
        employment_status=record.employment_status,
        company_name=record.company_name,
        created_at=record.created_at,
    )
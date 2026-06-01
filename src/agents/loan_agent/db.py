from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone
import os

DATABASE_URL = os.getenv("LOAN_DB_URL", "sqlite:///./loan.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class LoanRecord(Base):
    __tablename__ = "loans"

    loan_id              = Column(String, primary_key=True)
    borrower_id          = Column(String, nullable=False)
    loan_amount          = Column(Float, nullable=False)
    loan_term_months     = Column(Integer, nullable=False)
    purpose              = Column(String, nullable=False)
    collateral_type      = Column(String, nullable=True)
    collateral_value     = Column(Float, nullable=True)
    ltv_ratio            = Column(Float, nullable=True)
    debt_service_ratio   = Column(Float, nullable=True)
    status               = Column(String, default="pending")
    created_at           = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
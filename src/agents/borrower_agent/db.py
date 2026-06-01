# SQLAlchemy setup for borrower persistence
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone
import os

DATABASE_URL = os.getenv("BORROWER_DB_URL", "sqlite:///./borrower.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class BorrowerRecord(Base):
    __tablename__ = "borrowers"

    borrower_id       = Column(String, primary_key=True)
    name              = Column(String, nullable=False)
    email             = Column(String, nullable=False, unique=True)
    annual_income     = Column(Float, nullable=False)
    credit_score      = Column(Integer, nullable=False)
    employment_status = Column(String, nullable=False)
    company_name      = Column(String, nullable=True)
    created_at        = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
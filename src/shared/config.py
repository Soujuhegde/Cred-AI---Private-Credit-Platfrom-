# Environment configuration - all agents import this
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "secret-internal-key")

# Agent base URLs (override via env for Docker/prod)
BORROWER_AGENT_URL  = os.getenv("BORROWER_AGENT_URL",  "http://localhost:8001")
LOAN_AGENT_URL      = os.getenv("LOAN_AGENT_URL",      "http://localhost:8002")
CREDIT_AGENT_URL    = os.getenv("CREDIT_AGENT_URL",    "http://localhost:8003")

LLM_MODEL    = os.getenv("LLM_MODEL", "gpt-4o")
EMBED_MODEL  = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHROMA_PATH  = os.getenv("CHROMA_PATH", "./chroma_db")
LOG_LEVEL    = os.getenv("LOG_LEVEL", "INFO")
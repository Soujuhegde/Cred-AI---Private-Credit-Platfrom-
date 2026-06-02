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
async def rag_query(q: str, n: int = 1):
    """RAG retrieval endpoint — semantic search + LLM synthesis."""
    results = query_intelligence(q, n_results=n)
    
    answer = "I am sorry, but I could not find any matching credit intelligence records in the verified database to answer your question."
    if results:
        from .handlers import _llm
        from shared.config import LLM_MODEL
        
        # Construct verified fragments context with pure Source tag
        context_str = ""
        for idx, item in enumerate(results):
            context_str += f"[Source] Document content: {item['text']}\n"
            
        prompt = f"""You are a helpful senior private credit analyst. Answer the user's question using ONLY the provided verified context fragments.
        
IMPORTANT: Keep the tone highly supportive, professional, and clear. Explain any banking term simply if used.
If the context does not contain enough information to answer the question, state: "I'm sorry, but the verified database does not contain information to answer that question."
Under no circumstances may you fabricate facts, statistics, names, or assumptions. 
For every claim you make, append the corresponding Source tag (e.g. [Source]) at the end of the sentence to show where the fact came from.

User Question: {q}

Verified Context Fragments:
{context_str}

Grounded Answer:"""

        try:
            response = _llm.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )
            raw_answer = response.choices[0].message.content or ""
            import re
            answer = re.sub(r"<think>.*?(?:</think>|$)", "", raw_answer, flags=re.DOTALL).strip()
        except Exception as e:
            answer = f"Error generating grounded answer: {e}"

    return {"query": q, "results": results, "answer": answer}
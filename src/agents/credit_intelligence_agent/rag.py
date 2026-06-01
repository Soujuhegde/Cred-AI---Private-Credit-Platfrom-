# ChromaDB RAG store — embeddings + retrieval for credit intelligence
import logging
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from shared.config import CHROMA_PATH

logger = logging.getLogger(__name__)

_client: chromadb.PersistentClient | None = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)

        # Free local model — downloads once (~90MB), runs entirely offline
        # Best free model for English financial text:
        embed_fn = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"   # fast, 384-dim, great for semantic search
            # Alternatives:
            # "BAAI/bge-small-en-v1.5"      # slightly better quality, same size
            # "paraphrase-multilingual-MiniLM-L12-v2"  # if you need Hindi + English
        )
        _collection = _client.get_or_create_collection(
            name="credit_intelligence",
            embedding_function=embed_fn,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def upsert_intelligence(doc_id: str, text: str, metadata: dict) -> None:
    """Store or update a credit intelligence document."""
    col = _get_collection()
    col.upsert(documents=[text], ids=[doc_id], metadatas=[metadata])
    logger.info("Upserted RAG doc %s", doc_id)


def query_intelligence(query_text: str, n_results: int = 3) -> list[dict]:
    """Retrieve top-k relevant credit intelligence chunks."""
    col = _get_collection()
    results = col.query(query_texts=[query_text], n_results=n_results)
    out = []
    for i, doc in enumerate(results["documents"][0]):
        out.append({
            "text": doc,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return out
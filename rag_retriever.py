"""
rag_retriever.py
----------------
Module for loading the FAISS vector database and retrieving
relevant maintenance procedures based on detected machine conditions.
Configured via config.py.
"""

import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from config import INDEX_PATH, DOCS_PATH, EMBEDDING_MODEL_NAME, RAG_TOP_K

_model = None
_index = None
_documents = None

def init_rag():
    """Lazily loads and caches the RAG embedding model and FAISS index."""
    global _model, _index, _documents
    if _model is not None and _index is not None and _documents is not None:
        return

    print("Loading RAG resources (Embedding Model & FAISS Index)...")
    if not os.path.exists(INDEX_PATH) or not os.path.exists(DOCS_PATH):
        raise FileNotFoundError(f"RAG files not found at {INDEX_PATH} or {DOCS_PATH}. Run create_vector_db.py first.")

    _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    _index = faiss.read_index(INDEX_PATH)
    with open(DOCS_PATH, "rb") as f:
        _documents = pickle.load(f)

    print(f"[OK] RAG Initialized: {_index.ntotal} maintenance documents indexed.\n")

def search_maintenance_knowledge(query_text: str, top_k: int = RAG_TOP_K) -> list[str]:
    """
    Encodes query text and searches FAISS vector index for top_k closest matches.
    """
    init_rag()
    query_vector = _model.encode([query_text], convert_to_numpy=True, normalize_embeddings=True)
    distances, indices = _index.search(query_vector, top_k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(_documents):
            results.append(_documents[idx])
    return results

def get_maintenance_for_conditions(conditions: list[str], top_k: int = RAG_TOP_K) -> str:
    """
    Takes detected sensor conditions from diagnosis.py, searches the FAISS index,
    and returns formatted maintenance knowledge.
    """
    if not conditions or conditions == ["No major abnormal sensor condition detected"]:
        return ""

    query = " ".join(conditions)
    matched_docs = search_maintenance_knowledge(query, top_k=top_k)

    if matched_docs:
        return matched_docs[0]
    return "No matching maintenance knowledge found."

if __name__ == "__main__":
    print("--- Testing RAG Retriever with Sample Conditions ---")
    test_conditions = ["High torque"]
    print(f"Input Conditions: {test_conditions}")

    advice = get_maintenance_for_conditions(test_conditions, top_k=1)
    print("\nRetrieved Maintenance Knowledge:")
    print("=" * 60)
    print(advice)
    print("=" * 60)

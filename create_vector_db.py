"""
create_vector_db.py
-------------------
Parses the industrial maintenance knowledge base, creates semantic embeddings
using sentence-transformers (all-MiniLM-L6-v2), and builds a FAISS vector index.
Saves:
- rag/maintenance.index (FAISS vector index)
- rag/documents.pkl (Serialized document chunks)
"""

import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer

KNOWLEDGE_FILE = "knowledge_base/maintenance_knowledge.txt"
INDEX_PATH = "rag/maintenance.index"
DOCS_PATH = "rag/documents.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

def build_vector_database():
    print(f"Reading knowledge base from: {KNOWLEDGE_FILE}")
    if not os.path.exists(KNOWLEDGE_FILE):
        raise FileNotFoundError(f"{KNOWLEDGE_FILE} not found!")

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Split documents by "TOPIC:"
    raw_topics = content.split("TOPIC:")
    documents = []

    for chunk in raw_topics:
        cleaned = chunk.strip()
        if cleaned and not cleaned.startswith("==="):
            documents.append("TOPIC: " + cleaned)

    print(f"Extracted {len(documents)} maintenance topic documents:")
    for i, doc in enumerate(documents, 1):
        first_line = doc.split("\n")[0]
        print(f"  {i}. {first_line}")

    # Load sentence transformer model
    print(f"\nLoading SentenceTransformer model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    # Generate embeddings
    print("Generating embeddings for documents...")
    embeddings = model.encode(documents, convert_to_numpy=True, normalize_embeddings=True)
    dim = embeddings.shape[1]
    print(f"Embedding shape: {embeddings.shape} (Dimension: {dim})")

    # Build FAISS Index (IndexFlatIP for cosine similarity on normalized vectors)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"Indexed {index.ntotal} vectors into FAISS.")

    # Save to disk
    os.makedirs("rag", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(DOCS_PATH, "wb") as f:
        pickle.dump(documents, f)

    print(f"\n[OK] Vector DB successfully built and saved to:")
    print(f"   - {INDEX_PATH}")
    print(f"   - {DOCS_PATH}")

if __name__ == "__main__":
    build_vector_database()

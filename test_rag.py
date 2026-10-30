"""
test_rag.py
-----------
Standalone test script to verify FAISS vector search against the maintenance knowledge base.
"""

from rag_retriever import search_maintenance_knowledge

def main():
    print("=" * 60)
    print("RAG Semantic Search Test")
    print("=" * 60)
    
    while True:
        query = input("\nEnter query (or 'quit' to exit): ").strip()
        if not query or query.lower() == "quit":
            break
            
        results = search_maintenance_knowledge(query, top_k=3)
        print(f"\nTop {len(results)} Retrieval Results:")
        for i, doc in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(doc)
            print("-" * 40)

if __name__ == "__main__":
    main()

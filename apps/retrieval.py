import time
import os
from typing import List, Dict
from pinecone import Pinecone

from apps.config import (
PINECONE_API_KEY,
PINECONE_INDEX_NAME,
PINECONE_NAMESPACE,
PINECONE_CLOUD,
PINECONE_REGION,
PINECONE_EMBED_MODEL,
TOP_K, 
RERANK_TOP_N
)

_pc = Pinecone(api_key=PINECONE_API_KEY)

#_pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))



def search(query: str, top_k: int = TOP_K) -> List[Dict]:

    index = _pc.Index(PINECONE_INDEX_NAME)
    
    results = index.search(
        namespace=PINECONE_NAMESPACE,
        query={
            "top_k": top_k,
            "inputs": {"text": query},
        },
        fields=["chunk_text", "source", "pages"]
    )

    hits = []

    for item in results.get("result", {}).get("hits", []):
        fields = item.get("fields", {})
        hits.append(
            {
                "id": item.get("_id", ""),
                "score": item.get("_score", 0.0),
                "chunk_text": fields.get("chunk_text", ""),
                "source": fields.get("source", ""),
                "pages": fields.get("pages", ""),
            }
        )

    return hits


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run retrieval test against Pinecone index")
    parser.add_argument("--query", type=str, default="growth in last 3 months")
    parser.add_argument("--top-k", type=int, default=TOP_K)
    args = parser.parse_args()

    try:
        retrieved = search(args.query, args.top_k)
        print(f"Found {len(retrieved)} hit(s) for query: {args.query!r}")
        for i, hit in enumerate(retrieved, start=1):
            print(f"\n[{i}] score={hit['score']}")
            print(f"id={hit['id']}")
            print(f"source={hit['source']} pages={hit['pages']}")
            print(f"text={hit['chunk_text'][:240]}")
    except Exception as e:
        print(f"Retrieval test failed: {e}")
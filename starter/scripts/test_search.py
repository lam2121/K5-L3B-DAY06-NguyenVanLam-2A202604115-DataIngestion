"""Interactive CLI script to manually test retrieval against the vector database."""
import argparse
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from src.embeddings import MyEmbedder
from src.store import PgVectorStore


def main():
    parser = argparse.ArgumentParser(description="Test manual semantic retrieval.")
    parser.add_argument("query", type=str, nargs="?", default="What is the definition of procrastination?", help="Search query question")
    parser.add_argument("--strategy", type=str, default="B", choices=["A", "B", "C", "hybrid"], help="Strategy (A, B, C, hybrid)")
    parser.add_argument("--chapter", type=int, default=None, help="Optional chapter filter (for Strategy C/hybrid)")
    parser.add_argument("--top-k", type=int, default=3, help="Number of results to return")

    args = parser.parse_args()

    print(f"\nSearching Strategy {args.strategy} for: \"{args.query}\"")
    if (args.strategy in ("C", "hybrid")) and args.chapter is not None:
        filters = {"chapter": args.chapter}
        print(f"Applying metadata filter: {filters}")
    else:
        filters = None

    db_url = "postgresql://day6:day6_local_only@127.0.0.1:55433/day6_lab"
    embedder = MyEmbedder("all-MiniLM-L6-v2")
    store = PgVectorStore(db_url, dimensions=384)

    if args.strategy == "hybrid":
        import json
        from src.hybrid import HybridRetriever
        from src.models import Chunk
        chunks_json = base_dir / "results" / "chunks_strategy_B.json"
        if not chunks_json.exists():
            chunks_json = base_dir.parent / "results" / "chunks_strategy_B.json"
        if chunks_json.exists():
            with open(chunks_json, "r", encoding="utf-8") as f:
                raw = json.load(f)
            chunks = [
                Chunk(
                    chunk_id=c["chunk_id"],
                    document_id=c["document_id"],
                    source=c["source"],
                    page=c["page"],
                    text=c["text"],
                    metadata=c["metadata"]
                )
                for c in raw
            ]
        else:
            import psycopg
            with psycopg.connect(db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT chunk_id, document_id, source, page, text, metadata FROM document_chunks WHERE strategy = 'B';")
                    rows = cur.fetchall()
                    chunks = [Chunk(chunk_id=r[0], document_id=r[1], source=r[2], page=r[3], text=r[4], metadata=r[5]) for r in rows]
        retriever = HybridRetriever(chunks=chunks, store=store, embedder=embedder)
        results = retriever.search_hybrid(query=args.query, top_k=args.top_k, method="weighted", alpha=0.5, filters=filters)
    else:
        q_vec = embedder.embed_query(args.query)
        search_strat = "B" if args.strategy == "C" else args.strategy
        results = store.search(strategy=search_strat, query_vector=q_vec, top_k=args.top_k, filters=filters)

    print("\n" + "=" * 80)
    print(f"TOP-{len(results)} RETRIEVED CHUNKS")
    print("=" * 80)

    for idx, r in enumerate(results, start=1):
        print(f"\n[Rank {idx}] Chunk ID: {r['chunk_id']} | Page: {r['page']} | Score: {r['score']}")
        print(f"Metadata: {r['metadata']}")
        print("-" * 80)
        print(r["text"])
        print("-" * 80)


if __name__ == "__main__":
    main()


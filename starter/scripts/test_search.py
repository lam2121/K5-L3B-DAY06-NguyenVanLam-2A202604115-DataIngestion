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
    parser.add_argument("--strategy", type=str, default="B", choices=["A", "B", "C"], help="Strategy (A, B, C)")
    parser.add_argument("--chapter", type=int, default=None, help="Optional chapter filter (for Strategy C)")
    parser.add_argument("--top-k", type=int, default=3, help="Number of results to return")

    args = parser.parse_args()

    print(f"\nSearching Strategy {args.strategy} for: \"{args.query}\"")
    if args.strategy == "C" and args.chapter is not None:
        filters = {"chapter": args.chapter}
        print(f"Applying metadata filter: {filters}")
    else:
        filters = None

    db_url = "postgresql://day6:day6_local_only@127.0.0.1:55433/day6_lab"
    embedder = MyEmbedder("all-MiniLM-L6-v2")
    store = PgVectorStore(db_url, dimensions=384)

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


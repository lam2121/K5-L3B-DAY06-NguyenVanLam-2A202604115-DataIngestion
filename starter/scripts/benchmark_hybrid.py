"""Benchmark Hybrid Retrieval across different fusion methods and parameters."""
import json
import logging
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from src.embeddings import MyEmbedder
from src.evaluation import evaluate_query, summarize
from src.hybrid import HybridRetriever
from src.models import Chunk
from src.store import PgVectorStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

base_dir = Path(__file__).resolve().parent.parent
bench_path = base_dir / "data" / "benchmark.json"
chunks_path = base_dir / "results" / "chunks_strategy_B.json"

with open(bench_path, "r", encoding="utf-8") as f:
    benchmark_questions = json.load(f)

with open(chunks_path, "r", encoding="utf-8") as f:
    raw_chunks = json.load(f)

chunks = [
    Chunk(
        chunk_id=c["chunk_id"],
        document_id=c["document_id"],
        source=c["source"],
        page=c["page"],
        text=c["text"],
        metadata=c["metadata"]
    )
    for c in raw_chunks
]

logger.info("Loaded %d chunks and %d questions.", len(chunks), len(benchmark_questions))

db_url = "postgresql://day6:day6_local_only@127.0.0.1:55433/day6_lab"
embedder = MyEmbedder("all-MiniLM-L6-v2")
store = PgVectorStore(db_url, dimensions=384)

hybrid_retriever = HybridRetriever(chunks=chunks, store=store, embedder=embedder)

experiments = [
    {"name": "BM25-only", "method": "weighted", "alpha": 0.0},
    {"name": "Dense-only (Strategy C)", "method": "weighted", "alpha": 1.0},
    {"name": "Weighted (alpha=0.3)", "method": "weighted", "alpha": 0.3},
    {"name": "Weighted (alpha=0.5)", "method": "weighted", "alpha": 0.5},
    {"name": "Weighted (alpha=0.7)", "method": "weighted", "alpha": 0.7},
    {"name": "RRF (k=60)", "method": "rrf", "alpha": None}
]

results_table = []
all_exp_traces = {}

for exp in experiments:
    exp_name = exp["name"]
    method = exp["method"]
    alpha = exp["alpha"]

    traces = []
    for q in benchmark_questions:
        filt = q.get("filter")
        if method == "rrf":
            hits = hybrid_retriever.search_hybrid(
                query=q["question"],
                top_k=3,
                method="rrf",
                filters=filt
            )
        else:
            hits = hybrid_retriever.search_hybrid(
                query=q["question"],
                top_k=3,
                method="weighted",
                alpha=alpha,
                filters=filt
            )
        trace = evaluate_query(q, hits)
        traces.append(trace)

    all_exp_traces[exp_name] = traces
    summary = summarize(traces)

    results_table.append({
        "name": exp_name,
        "dev_hit1": summary["dev"]["hit1_fraction"],
        "dev_hit3": summary["dev"]["hit3_fraction"],
        "test_hit1": summary["test"]["hit1_fraction"],
        "test_hit3": summary["test"]["hit3_fraction"],
    })

print("\n" + "=" * 80)
print("HYBRID RETRIEVAL PARAMETER TUNING ON DEV & EVALUATION ON TEST")
print("=" * 80)
print(f"{'Method / Configuration':<28} | {'Dev Hit@1':<10} | {'Dev Hit@3':<12} | {'Test Hit@1':<11} | {'Test Hit@3':<11}")
print("-" * 80)
for r in results_table:
    print(f"{r['name']:<28} | {r['dev_hit1']:<10} | {r['dev_hit3']:<12} | {r['test_hit1']:<11} | {r['test_hit3']:<11}")
print("=" * 80)

# Save hybrid traces
out_path = base_dir / "results" / "hybrid_traces.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"summary": results_table, "traces": all_exp_traces}, f, ensure_ascii=False, indent=2)

root_out_path = base_dir.parent / "results" / "hybrid_traces.json"
with open(root_out_path, "w", encoding="utf-8") as f:
    json.dump({"summary": results_table, "traces": all_exp_traces}, f, ensure_ascii=False, indent=2)

print("\nSaved hybrid results to", out_path)

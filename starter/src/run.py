"""Pipeline orchestrator for Day 06 Data Ingestion Lab."""
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

from .chunking import by_paragraph, fixed_size
from .embeddings import MyEmbedder
from .evaluation import evaluate_query, summarize
from .ingestion import load_pdf
from .store import PgVectorStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    # 1. Load configuration
    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(base_dir / ".env")
    if not (base_dir / ".env").exists() and (base_dir / "starter" / ".env").exists():
        load_dotenv(base_dir / "starter" / ".env")

    db_url = os.getenv("DATABASE_URL", "postgresql://day6:day6_local_only@127.0.0.1:55433/day6_lab")
    model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    pdf_path = base_dir / "data" / "College_Success_web.pdf"
    if not pdf_path.exists() and (base_dir / "starter" / "data" / "College_Success_web.pdf").exists():
        pdf_path = base_dir / "starter" / "data" / "College_Success_web.pdf"

    benchmark_path = base_dir / "data" / "benchmark.json"
    if not benchmark_path.exists() and (base_dir / "benchmark" / "benchmark.json").exists():
        benchmark_path = base_dir / "benchmark" / "benchmark.json"
    results_dir = base_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    exp_log_path = base_dir.parent / "artifacts" / "experiment_log.csv"

    if not pdf_path.exists():
        raise FileNotFoundError(f"Corpus PDF not found at {pdf_path}")
    if not benchmark_path.exists():
        raise FileNotFoundError(f"Benchmark not found at {benchmark_path}")

    # 2. Initialize Embedder and Store
    logger.info("Initializing Embedder with model: %s", model_name)
    embedder = MyEmbedder(model_name)
    logger.info("Embedder initialized. Dimensions: %d", embedder.dimensions)

    logger.info("Connecting to PgVectorStore at %s", db_url)
    store = PgVectorStore(database_url=db_url, dimensions=embedder.dimensions)
    store.create_schema()

    # 3. Load Corpus Pages (Pages 11 to 292 covering Preface and Chapters 1 to 8, > 280 pages)
    logger.info("Loading document pages from %s (covering benchmark chapters 0-8)...", pdf_path.name)
    doc_id = "openstax-college-success"
    source_path = "starter/data/College_Success_web.pdf"
    pages = load_pdf(pdf_path, document_id=doc_id, source=source_path, start_page=11, end_page=292)
    logger.info("Loaded %d pages from corpus.", len(pages))

    # 4. Load Benchmark Questions
    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_questions = json.load(f)
    logger.info("Loaded %d benchmark questions.", len(benchmark_questions))

    # 5. Ingestion Strategies
    strategies = [
        {
            "name": "A",
            "chunk_fn": lambda p: fixed_size(p, size=500, overlap=50),
            "use_filter": False,
            "desc": "Fixed-size (500 chars, overlap 50, no filter)"
        },
        {
            "name": "B",
            "chunk_fn": lambda p: by_paragraph(p, max_size=800),
            "use_filter": False,
            "desc": "By-paragraph (max 800 chars, no filter)"
        },
        {
            "name": "C",
            "chunk_fn": lambda p: by_paragraph(p, max_size=800),
            "use_filter": True,
            "desc": "By-paragraph (max 800 chars, with metadata filter)"
        }
    ]

    all_traces: dict[str, list[dict]] = {}
    strategy_metrics: dict[str, dict] = {}
    strategy_stats: dict[str, dict] = {}

    # Pre-build chunks for B/C to reuse and save time
    para_chunks = []
    for p in pages:
        para_chunks.extend(by_paragraph(p, max_size=800))

    fixed_chunks = []
    for p in pages:
        fixed_chunks.extend(fixed_size(p, size=500, overlap=50))

    logger.info("Generated %d fixed chunks for Strategy A.", len(fixed_chunks))
    logger.info("Generated %d paragraph chunks for Strategy B & C.", len(para_chunks))

    # Ingest into Postgres
    # Strategy A
    t0 = time.time()
    logger.info("Ingesting Strategy A into vector store...")
    fixed_texts = [c.text for c in fixed_chunks]
    fixed_vectors = embedder.embed_documents(fixed_texts)
    store.upsert("A", fixed_chunks, fixed_vectors)
    ingest_time_a = time.time() - t0
    strategy_stats["A"] = {"chunk_count": len(fixed_chunks), "ingest_time_sec": round(ingest_time_a, 2)}

    # Strategy B
    t0 = time.time()
    logger.info("Ingesting Strategy B into vector store...")
    para_texts = [c.text for c in para_chunks]
    para_vectors = embedder.embed_documents(para_texts)
    store.upsert("B", para_chunks, para_vectors)
    ingest_time_b = time.time() - t0
    strategy_stats["B"] = {"chunk_count": len(para_chunks), "ingest_time_sec": round(ingest_time_b, 2)}

    # Strategy C reuses Strategy B's index, but queries with metadata filter
    strategy_stats["C"] = {"chunk_count": len(para_chunks), "ingest_time_sec": round(ingest_time_b, 2)}

    # 6. Run Benchmark for each Strategy
    for strat in strategies:
        s_name = strat["name"]
        use_filter = strat["use_filter"]
        logger.info("Running benchmark on Strategy %s (%s)...", s_name, strat["desc"])

        traces = []
        t_start = time.time()
        for q in benchmark_questions:
            q_vec = embedder.embed_query(q["question"])
            filt = q.get("filter") if use_filter else None
            # For C, store table query points to strategy 'B' data if sharing, or 'B' with filter!
            search_strat = "B" if s_name == "C" else s_name
            hits = store.search(strategy=search_strat, query_vector=q_vec, top_k=3, filters=filt)
            trace = evaluate_query(q, hits)
            traces.append(trace)

        bench_time = time.time() - t_start
        all_traces[s_name] = traces
        summary = summarize(traces)
        summary["benchmark_time_sec"] = round(bench_time, 2)
        strategy_metrics[s_name] = summary

        logger.info(
            "Strategy %s Results: Dev Hit@1=%s, Hit@3=%s | Test Hit@1=%s, Hit@3=%s",
            s_name,
            summary["dev"]["hit1_fraction"],
            summary["dev"]["hit3_fraction"],
            summary["test"]["hit1_fraction"],
            summary["test"]["hit3_fraction"]
        )

    # 7. Save Traces and Metrics
    output_traces = results_dir / "traces.json"
    with open(output_traces, "w", encoding="utf-8") as f:
        json.dump(all_traces, f, ensure_ascii=False, indent=2)
    logger.info("Saved complete traces to %s", output_traces)

    output_metrics = results_dir / "metrics.json"
    with open(output_metrics, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model": model_name,
                "dimensions": embedder.dimensions,
                "stats": strategy_stats,
                "metrics": strategy_metrics
            },
            f,
            ensure_ascii=False,
            indent=2
        )
    logger.info("Saved summary metrics to %s", output_metrics)

    # 8. Update artifacts/experiment_log.csv
    exp_rows = [
        {
            "strategy": "A",
            "chunking": "fixed_size",
            "chunk_size": 500,
            "overlap": 50,
            "metadata": "source;page;chapter",
            "filter": "none",
            "vectorizer": f"{model_name} ({embedder.dimensions}d)",
            "hypothesis": "Fixed-size chunks may split sentences across boundaries, reducing coherence and evidence recall.",
            "dev_hit1": strategy_metrics["A"]["dev"]["hit1_fraction"],
            "dev_hit3": strategy_metrics["A"]["dev"]["hit3_fraction"],
            "test_hit1": strategy_metrics["A"]["test"]["hit1_fraction"],
            "test_hit3": strategy_metrics["A"]["test"]["hit3_fraction"],
            "notes": f"Chunks: {strategy_stats['A']['chunk_count']}, Ingest: {strategy_stats['A']['ingest_time_sec']}s, Cost: 0 USD"
        },
        {
            "strategy": "B",
            "chunking": "by_paragraph",
            "chunk_size": 800,
            "overlap": 0,
            "metadata": "source;page;chapter",
            "filter": "none",
            "vectorizer": f"{model_name} ({embedder.dimensions}d)",
            "hypothesis": "Paragraph-based chunking preserves complete semantic units and sentences, improving coherence and grounding.",
            "dev_hit1": strategy_metrics["B"]["dev"]["hit1_fraction"],
            "dev_hit3": strategy_metrics["B"]["dev"]["hit3_fraction"],
            "test_hit1": strategy_metrics["B"]["test"]["hit1_fraction"],
            "test_hit3": strategy_metrics["B"]["test"]["hit3_fraction"],
            "notes": f"Chunks: {strategy_stats['B']['chunk_count']}, Ingest: {strategy_stats['B']['ingest_time_sec']}s, Cost: 0 USD"
        },
        {
            "strategy": "C",
            "chunking": "by_paragraph",
            "chunk_size": 800,
            "overlap": 0,
            "metadata": "source;page;chapter",
            "filter": "chapter (when specified)",
            "vectorizer": f"{model_name} ({embedder.dimensions}d)",
            "hypothesis": "Metadata filtering restricts retrieval to target chapter, preventing cross-chapter distraction on filter questions.",
            "dev_hit1": strategy_metrics["C"]["dev"]["hit1_fraction"],
            "dev_hit3": strategy_metrics["C"]["dev"]["hit3_fraction"],
            "test_hit1": strategy_metrics["C"]["test"]["hit1_fraction"],
            "test_hit3": strategy_metrics["C"]["test"]["hit3_fraction"],
            "notes": f"Reuses B chunks ({strategy_stats['C']['chunk_count']}), SQL JSONB chapter filtering, Cost: 0 USD"
        }
    ]

    with open(exp_log_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "strategy", "chunking", "chunk_size", "overlap", "metadata",
            "filter", "vectorizer", "hypothesis", "dev_hit1", "dev_hit3",
            "test_hit1", "test_hit3", "notes"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(exp_rows)

    logger.info("Updated experiment log at %s", exp_log_path)

    # 9. Print Final Comparison Table
    print("\n" + "=" * 80)
    print("DAY 06 EXPERIMENT RESULTS SUMMARY")
    print("=" * 80)
    print(f"{'Strategy':<10} | {'Split':<6} | {'Hit@1':<8} | {'Evidence Hit@3':<14} | {'Chunks':<8} | {'Cost':<6}")
    print("-" * 80)
    for s_name in ["A", "B", "C"]:
        m = strategy_metrics[s_name]
        cnt = strategy_stats[s_name]["chunk_count"]
        print(f"{s_name:<10} | {'dev':<6} | {m['dev']['hit1_fraction']:<8} | {m['dev']['hit3_fraction']:<14} | {cnt:<8} | {'$0':<6}")
        print(f"{s_name:<10} | {'test':<6} | {m['test']['hit1_fraction']:<8} | {m['test']['hit3_fraction']:<14} | {cnt:<8} | {'$0':<6}")
        print("-" * 80)


if __name__ == "__main__":
    main()

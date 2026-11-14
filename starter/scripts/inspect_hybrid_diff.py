import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
with open(base_dir / "results" / "hybrid_traces.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dense_traces = {t["question_id"]: t for t in data["traces"]["Dense-only (Strategy C)"]}
hybrid_traces = {t["question_id"]: t for t in data["traces"]["Weighted (alpha=0.5)"]}
rrf_traces = {t["question_id"]: t for t in data["traces"]["RRF (k=60)"]}

print("=== DIFFERENCES: Dense (Strategy C) vs Hybrid (Weighted alpha=0.5) ===")
improved = []
degraded = []

for qid in sorted(dense_traces.keys()):
    dt = dense_traces[qid]
    ht = hybrid_traces[qid]
    d1, d3 = dt["hit_at_1"], dt["hit_at_3"]
    h1, h3 = ht["hit_at_1"], ht["hit_at_3"]

    if (d1, d3) != (h1, h3):
        print(f"\n[{qid}] ({dt['split']}) {dt['question']}")
        print(f"  Gold page: {dt['gold_page']}")
        print(f"  Dense (C) : Hit@1={d1}, Hit@3={d3} | Pages: {[h['page'] for h in dt['hits'][:3]]}")
        print(f"  Hybrid 0.5: Hit@1={h1}, Hit@3={h3} | Pages: {[h['page'] for h in ht['hits'][:3]]}")

        # Check if improved or degraded
        if (not d3 and h3) or (not d1 and h1 and d3 == h3):
            improved.append(qid)
        elif (d3 and not h3) or (d1 and not h1):
            degraded.append(qid)

print("\n" + "=" * 50)
print("Improved questions:", improved)
print("Degraded questions (làm xấu kết quả):", degraded)

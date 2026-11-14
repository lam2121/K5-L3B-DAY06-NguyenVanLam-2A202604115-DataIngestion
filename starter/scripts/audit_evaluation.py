import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
traces_path = base_dir / "results" / "traces.json"

with open(traces_path, "r", encoding="utf-8") as f:
    traces = json.load(f)

print("=== Analyzing 5 Test Queries across Strategies ===")
test_q_ids = ["q16", "q17", "q18", "q19", "q20"]

for s in ["A", "B", "C"]:
    print(f"\n--- Strategy {s} ---")
    s_traces = {t["question_id"]: t for t in traces[s] if t["split"] == "test"}
    for qid in test_q_ids:
        t = s_traces[qid]
        print(f"\n[{qid}] {t['question']}")
        print(f"  Gold page: {t['gold_page']}, Filter: {t.get('filter')}")
        print(f"  Hit@1: {t['hit_at_1']}, Hit@3: {t['hit_at_3']}")
        for hit in t["hits"][:3]:
            print(f"    Rank {hit['rank']}: Page {hit['page']}, Score {hit['score']}, Hit={hit['is_hit']}")
            print(f"      Text snippet: {repr(hit['text'][:120])}")
            print(f"      Metadata: {hit['metadata']}")


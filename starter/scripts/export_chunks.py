"""Export all chunks from PostgreSQL to JSON files for manual inspection and testing."""
import json
from pathlib import Path
import psycopg
from psycopg.rows import dict_row

base_dir = Path(__file__).resolve().parent.parent
db_url = "postgresql://day6:day6_local_only@127.0.0.1:55433/day6_lab"
results_dir = base_dir / "results"
results_dir.mkdir(parents=True, exist_ok=True)
root_results_dir = base_dir.parent / "results"
root_results_dir.mkdir(parents=True, exist_ok=True)

with psycopg.connect(db_url) as conn:
    with conn.cursor(row_factory=dict_row) as cur:
        # Export Strategy A
        cur.execute(
            """
            SELECT chunk_id, document_id, source, page, text, metadata
            FROM document_chunks
            WHERE strategy = 'A'
            ORDER BY page ASC, chunk_id ASC;
            """
        )
        chunks_a = cur.fetchall()

        # Export Strategy B
        cur.execute(
            """
            SELECT chunk_id, document_id, source, page, text, metadata
            FROM document_chunks
            WHERE strategy = 'B'
            ORDER BY page ASC, chunk_id ASC;
            """
        )
        chunks_b = cur.fetchall()

print(f"Exported {len(chunks_a)} chunks for Strategy A.")
print(f"Exported {len(chunks_b)} chunks for Strategy B/C.")

# Save to results
files = [
    (results_dir / "chunks_strategy_A.json", chunks_a),
    (results_dir / "chunks_strategy_B.json", chunks_b),
    (root_results_dir / "chunks_strategy_A.json", chunks_a),
    (root_results_dir / "chunks_strategy_B.json", chunks_b)
]

for p, data in files:
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved to", p)


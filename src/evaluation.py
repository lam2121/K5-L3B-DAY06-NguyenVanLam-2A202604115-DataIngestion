"""Evaluate retrieved evidence and preserve per-query traces."""
import re
from typing import Any


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Check source/page and gold evidence; compute hit@1 and hit@3 trace."""
    gold_page = question.get("gold_page")
    evidence_quote = _normalize(question.get("evidence_quote", ""))

    hit_evals = []
    for rank, hit in enumerate(hits, start=1):
        hit_page = hit.get("page")
        hit_text = _normalize(hit.get("text", ""))

        page_match = (gold_page is None) or (hit_page == gold_page)
        
        # Exact quote containment or high word-overlap containment
        if evidence_quote in hit_text:
            evidence_match = True
        else:
            # Word-level containment check for partial sentence boundary splits
            quote_words = [w for w in re.findall(r"\w+", evidence_quote) if len(w) > 3]
            if quote_words:
                found_words = sum(1 for w in quote_words if w in hit_text)
                evidence_match = (found_words / len(quote_words)) >= 0.75
            else:
                evidence_match = False

        is_hit = page_match and evidence_match

        hit_evals.append({
            "rank": rank,
            "chunk_id": hit.get("chunk_id"),
            "page": hit_page,
            "score": hit.get("score"),
            "text": hit.get("text"),
            "metadata": hit.get("metadata", {}),
            "page_match": page_match,
            "evidence_match": evidence_match,
            "is_hit": is_hit
        })

    hit_at_1 = bool(hit_evals and hit_evals[0]["is_hit"])
    hit_at_3 = any(h["is_hit"] for h in hit_evals[:3])

    return {
        "question_id": question.get("id"),
        "split": question.get("split", "dev"),
        "type": question.get("type", "unknown"),
        "question": question.get("question"),
        "expected_answer": question.get("expected_answer"),
        "gold_page": gold_page,
        "evidence_quote": question.get("evidence_quote"),
        "filter": question.get("filter"),
        "hit_at_1": hit_at_1,
        "hit_at_3": hit_at_3,
        "hits": hit_evals
    }


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate Hit@1 and Evidence Hit@3 by split (dev / test)."""
    splits = ["dev", "test", "all"]
    summary: dict[str, Any] = {}

    for s in splits:
        if s == "all":
            group = traces
        else:
            group = [t for t in traces if t.get("split") == s]

        total = len(group)
        if total == 0:
            summary[s] = {
                "total": 0,
                "hit1_count": 0,
                "hit1_fraction": "0/0",
                "hit1_percentage": 0.0,
                "hit3_count": 0,
                "hit3_fraction": "0/0",
                "hit3_percentage": 0.0,
            }
            continue

        hit1_count = sum(1 for t in group if t.get("hit_at_1"))
        hit3_count = sum(1 for t in group if t.get("hit_at_3"))

        summary[s] = {
            "total": total,
            "hit1_count": hit1_count,
            "hit1_fraction": f"{hit1_count}/{total}",
            "hit1_percentage": round(hit1_count / total * 100, 2),
            "hit3_count": hit3_count,
            "hit3_fraction": f"{hit3_count}/{total}",
            "hit3_percentage": round(hit3_count / total * 100, 2),
        }

    return summary

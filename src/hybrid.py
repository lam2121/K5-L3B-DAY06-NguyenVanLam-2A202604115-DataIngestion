"""Hybrid Retrieval: Combining Dense Vector Search with BM25 Keyword Search."""
import re
from typing import Any
from rank_bm25 import BM25Okapi
from .embeddings import MyEmbedder
from .models import Chunk
from .store import PgVectorStore


def tokenize(text: str) -> list[str]:
    """Simple alphanumeric word tokenizer for BM25."""
    return [w.lower() for w in re.findall(r"\w+", text) if len(w) > 1]


class HybridRetriever:
    def __init__(self, chunks: list[Chunk], store: PgVectorStore, embedder: MyEmbedder) -> None:
        self.chunks = chunks
        self.chunk_map = {c.chunk_id: c for c in chunks}
        self.store = store
        self.embedder = embedder

        # Pre-tokenize all chunks for BM25
        self.tokenized_corpus = [tokenize(c.text) for c in self.chunks]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search_bm25(self, query: str, top_k: int = 20, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Run standalone BM25 search with optional metadata filtering."""
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)

        # Filter by metadata if requested
        candidates = []
        for idx, (chunk, score) in enumerate(zip(self.chunks, scores)):
            if filters:
                match = True
                for k, v in filters.items():
                    if str(chunk.metadata.get(k)) != str(v):
                        match = False
                        break
                if not match:
                    continue
            candidates.append((chunk, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = candidates[:top_k]

        results = []
        for chunk, score in top_candidates:
            results.append({
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "source": chunk.source,
                "page": chunk.page,
                "text": chunk.text,
                "metadata": chunk.metadata,
                "bm25_score": float(score)
            })
        return results

    def search_hybrid(
        self,
        query: str,
        top_k: int = 3,
        method: str = "rrf",
        alpha: float = 0.5,
        filters: dict[str, Any] | None = None,
        candidate_k: int = 20
    ) -> list[dict[str, Any]]:
        """Perform hybrid search combining Dense and BM25.

        Methods:
          - 'rrf': Reciprocal Rank Fusion: 1 / (60 + rank_dense) + 1 / (60 + rank_bm25)
          - 'weighted': alpha * dense_norm + (1 - alpha) * bm25_norm
        """
        # 1. Dense search
        q_vec = self.embedder.embed_query(query)
        dense_results = self.store.search(strategy="B", query_vector=q_vec, top_k=candidate_k, filters=filters)

        # 2. BM25 search
        bm25_results = self.search_bm25(query, top_k=candidate_k, filters=filters)

        # 3. Fusion
        fused_scores: dict[str, dict[str, Any]] = {}

        if method == "rrf":
            # Reciprocal Rank Fusion (k=60)
            k_rrf = 60.0
            for rank, r in enumerate(dense_results, start=1):
                cid = r["chunk_id"]
                if cid not in fused_scores:
                    fused_scores[cid] = {"info": r, "score": 0.0, "dense_rank": rank, "bm25_rank": None}
                fused_scores[cid]["score"] += 1.0 / (k_rrf + rank)

            for rank, r in enumerate(bm25_results, start=1):
                cid = r["chunk_id"]
                if cid not in fused_scores:
                    chunk = self.chunk_map[cid]
                    fused_scores[cid] = {
                        "info": {
                            "chunk_id": chunk.chunk_id,
                            "document_id": chunk.document_id,
                            "source": chunk.source,
                            "page": chunk.page,
                            "text": chunk.text,
                            "metadata": chunk.metadata
                        },
                        "score": 0.0,
                        "dense_rank": None,
                        "bm25_rank": rank
                    }
                fused_scores[cid]["bm25_rank"] = rank
                fused_scores[cid]["score"] += 1.0 / (k_rrf + rank)

        else:
            # Min-Max Normalized Weighted Fusion
            dense_scores = [r.get("score", 0.0) for r in dense_results]
            max_d = max(dense_scores) if dense_scores else 1.0
            min_d = min(dense_scores) if dense_scores else 0.0
            range_d = max_d - min_d if max_d > min_d else 1.0

            bm25_scores = [r["bm25_score"] for r in bm25_results]
            max_b = max(bm25_scores) if bm25_scores else 1.0
            min_b = min(bm25_scores) if bm25_scores else 0.0
            range_b = max_b - min_b if max_b > min_b else 1.0

            for r in dense_results:
                cid = r["chunk_id"]
                norm_d = (r.get("score", 0.0) - min_d) / range_d
                fused_scores[cid] = {"info": r, "score": alpha * norm_d, "dense_score": norm_d, "bm25_score": 0.0}

            for r in bm25_results:
                cid = r["chunk_id"]
                norm_b = (r["bm25_score"] - min_b) / range_b
                if cid not in fused_scores:
                    chunk = self.chunk_map[cid]
                    fused_scores[cid] = {
                        "info": {
                            "chunk_id": chunk.chunk_id,
                            "document_id": chunk.document_id,
                            "source": chunk.source,
                            "page": chunk.page,
                            "text": chunk.text,
                            "metadata": chunk.metadata
                        },
                        "score": (1.0 - alpha) * norm_b,
                        "dense_score": 0.0,
                        "bm25_score": norm_b
                    }
                else:
                    fused_scores[cid]["score"] += (1.0 - alpha) * norm_b
                    fused_scores[cid]["bm25_score"] = norm_b

        # Sort descending by fused score
        sorted_chunks = sorted(fused_scores.values(), key=lambda x: x["score"], reverse=True)
        top_hits = sorted_chunks[:top_k]

        final_results = []
        for item in top_hits:
            res = dict(item["info"])
            res["score"] = round(item["score"], 4)
            final_results.append(res)

        return final_results


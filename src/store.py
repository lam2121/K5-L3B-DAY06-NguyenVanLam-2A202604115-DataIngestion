"""Store and search vectors using PostgreSQL + pgvector."""
import json
import logging
from typing import Any
import psycopg
from psycopg.rows import dict_row
from .models import Chunk

logger = logging.getLogger(__name__)


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int) -> None:
        """Retain connection settings; validate model dimensions."""
        self.database_url = database_url
        self.dimensions = dimensions
        if self.dimensions <= 0:
            raise ValueError(f"Invalid dimensions: {self.dimensions}")

    def get_connection(self) -> psycopg.Connection:
        return psycopg.connect(self.database_url, autocommit=False)

    def create_schema(self) -> None:
        """Create table with vector column and metadata."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id SERIAL PRIMARY KEY,
                        strategy VARCHAR(20) NOT NULL,
                        chunk_id VARCHAR(120) NOT NULL,
                        document_id VARCHAR(100) NOT NULL,
                        source VARCHAR(255) NOT NULL,
                        page INTEGER NOT NULL,
                        text TEXT NOT NULL,
                        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                        embedding vector({self.dimensions}) NOT NULL,
                        CONSTRAINT uq_strategy_chunk UNIQUE (strategy, chunk_id)
                    );
                    """
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_chunks_strat_doc ON document_chunks(strategy, document_id);"
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_chunks_meta ON document_chunks USING gin(metadata);"
                )
            conn.commit()
        logger.info("Schema created or verified with vector(%d)", self.dimensions)

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Validate lengths/dimensions and write stable IDs without duplicates.

        When re-ingesting changed source documents, update or replace chunks.
        """
        if len(chunks) != len(vectors):
            raise ValueError(f"Chunks count ({len(chunks)}) does not match vectors count ({len(vectors)})")

        if not chunks:
            return

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Remove obsolete chunks for this strategy and document_ids to guarantee no duplicates
                doc_ids = list({c.document_id for c in chunks})
                cur.execute(
                    "DELETE FROM document_chunks WHERE strategy = %s AND document_id = ANY(%s);",
                    (strategy, doc_ids)
                )

                # Batch insert chunks
                insert_sql = """
                    INSERT INTO document_chunks 
                    (strategy, chunk_id, document_id, source, page, text, metadata, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector)
                    ON CONFLICT (strategy, chunk_id) DO UPDATE SET
                        text = EXCLUDED.text,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding;
                """
                for chunk, vec in zip(chunks, vectors):
                    if len(vec) != self.dimensions:
                        raise ValueError(f"Vector dimension {len(vec)} != store dimension {self.dimensions}")
                    vec_str = "[" + ",".join(str(x) for x in vec) + "]"
                    meta_json = json.dumps(chunk.metadata)
                    cur.execute(
                        insert_sql,
                        (
                            strategy,
                            chunk.chunk_id,
                            chunk.document_id,
                            chunk.source,
                            chunk.page,
                            chunk.text,
                            meta_json,
                            vec_str
                        )
                    )
            conn.commit()
        logger.info("Upserted %d chunks for strategy %s", len(chunks), strategy)

    def search(
        self,
        strategy: str,
        query_vector: list[float],
        top_k: int = 3,
        filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Filter permitted metadata in SQL, rank by cosine distance, return top-k."""
        if len(query_vector) != self.dimensions:
            raise ValueError(f"Query vector dimension {len(query_vector)} != store dimension {self.dimensions}")

        vec_str = "[" + ",".join(str(x) for x in query_vector) + "]"

        sql = """
            SELECT chunk_id, document_id, source, page, text, metadata,
                   (embedding <=> %s::vector) AS distance
            FROM document_chunks
            WHERE strategy = %s
        """
        params: list[Any] = [vec_str, strategy]

        if filters:
            for k, v in filters.items():
                if isinstance(v, (int, float)):
                    sql += " AND (metadata->>%s)::numeric = %s"
                    params.extend([str(k), v])
                else:
                    sql += " AND (metadata->>%s) = %s"
                    params.extend([str(k), str(v)])

        sql += " ORDER BY distance ASC LIMIT %s;"
        params.append(top_k)

        with self.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

        results = []
        for r in rows:
            dist = float(r["distance"])
            score = max(0.0, 1.0 - dist)
            results.append({
                "chunk_id": r["chunk_id"],
                "document_id": r["document_id"],
                "source": r["source"],
                "page": r["page"],
                "text": r["text"],
                "metadata": r["metadata"],
                "score": round(score, 4),
                "distance": round(dist, 4)
            })

        return results

"""PostgreSQL + pgvector storage for documents and their chunks."""

import psycopg
from pgvector.psycopg import register_vector

from app import config

_SCHEMA = f"""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id          SERIAL PRIMARY KEY,
    path        TEXT UNIQUE NOT NULL,      -- relative to DOCS_DIR
    file_hash   TEXT NOT NULL,             -- sha256, used to skip unchanged files
    indexed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id           BIGSERIAL PRIMARY KEY,
    document_id  INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index  INTEGER NOT NULL,
    content      TEXT NOT NULL,
    source       TEXT NOT NULL,            -- file name shown in citations
    page         INTEGER,
    slide        INTEGER,
    embedding    vector({config.EMBED_DIM}) NOT NULL
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);
"""


def connect() -> psycopg.Connection:
    conn = psycopg.connect(config.DATABASE_URL)
    register_vector(conn)
    return conn


def init_schema() -> None:
    # The extension must exist before register_vector() can look up the type.
    with psycopg.connect(config.DATABASE_URL, autocommit=True) as conn:
        conn.execute(_SCHEMA)

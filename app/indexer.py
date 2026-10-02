"""Load documents, embed their chunks and store them in PostgreSQL.

Re-running is cheap: unchanged files are skipped, changed files are re-indexed,
and files that were deleted from the folder are removed from the database.
"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from app import db
from app.chunking import chunk_sections
from app.embeddings import embed_documents
from app.loaders import iter_supported_files, load_file


@dataclass
class IndexReport:
    indexed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)
    chunks_added: int = 0


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index_folder(folder: Path, on_progress=print) -> IndexReport:
    db.init_schema()
    report = IndexReport()

    with db.connect() as conn:
        known = dict(conn.execute("SELECT path, file_hash FROM documents").fetchall())
        seen = set()

        for path in iter_supported_files(folder):
            rel = str(path.relative_to(folder))
            seen.add(rel)
            file_hash = _file_hash(path)
            if known.get(rel) == file_hash:
                report.unchanged.append(rel)
                continue

            try:
                chunks = chunk_sections(load_file(path))
                if not chunks:
                    raise ValueError("no text found (scanned PDF?)")
                on_progress(f"  embedding {rel} ({len(chunks)} chunks)…")
                vectors = embed_documents([c.text for c in chunks])
            except Exception as e:
                report.failed[rel] = str(e)
                continue

            with conn.transaction():
                conn.execute("DELETE FROM documents WHERE path = %s", (rel,))
                doc_id = conn.execute(
                    "INSERT INTO documents (path, file_hash) VALUES (%s, %s) RETURNING id",
                    (rel, file_hash),
                ).fetchone()[0]
                with conn.cursor() as cur:
                    cur.executemany(
                        """INSERT INTO chunks
                           (document_id, chunk_index, content, source, page, slide, embedding)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        [
                            (
                                doc_id,
                                i,
                                c.text.replace("\x00", ""),  # Postgres rejects NUL bytes
                                c.metadata["source"],
                                c.metadata.get("page"),
                                c.metadata.get("slide"),
                                np.array(v, dtype=np.float32),
                            )
                            for i, (c, v) in enumerate(zip(chunks, vectors))
                        ],
                    )
            conn.commit()  # save each file as we go, so an interruption loses little work
            report.indexed.append(rel)
            report.chunks_added += len(chunks)

        for rel in sorted(set(known) - seen):
            conn.execute("DELETE FROM documents WHERE path = %s", (rel,))
            report.removed.append(rel)
        conn.commit()

    return report

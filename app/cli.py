"""Command-line tools.

    python -m app.cli preview [folder]   show what text is extracted from your documents
    python -m app.cli index [folder]     embed documents and store them in PostgreSQL
"""

import argparse
from pathlib import Path

from app import config
from app.chunking import chunk_sections
from app.indexer import index_folder
from app.loaders import iter_supported_files, load_file


def _location(meta: dict) -> str:
    if "page" in meta:
        return f"page {meta['page']}"
    if "slide" in meta:
        return f"slide {meta['slide']}"
    return ""


def preview(folder: Path, show: int) -> None:
    files = list(iter_supported_files(folder))
    if not files:
        print(f"No supported files found in {folder}")
        return

    total = 0
    for path in files:
        try:
            chunks = chunk_sections(load_file(path))
        except Exception as e:
            print(f"\n✗ {path.name}: could not read ({e})")
            continue
        total += len(chunks)
        print(f"\n✓ {path.name}: {len(chunks)} chunks")
        for chunk in chunks[:show]:
            snippet = chunk.text[:160].replace("\n", " ")
            loc = _location(chunk.metadata)
            print(f"    [{loc or 'chunk ' + str(chunk.metadata['chunk'])}] {snippet}…")
    print(f"\n{len(files)} files, {total} chunks total")


def index(folder: Path) -> None:
    print(f"Indexing {folder}")
    r = index_folder(folder)
    for rel, err in r.failed.items():
        print(f"  ✗ {rel}: {err}")
    print(
        f"\nIndexed {len(r.indexed)} files ({r.chunks_added} chunks), "
        f"{len(r.unchanged)} unchanged, {len(r.removed)} removed, {len(r.failed)} failed"
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("preview", help="Show the text extracted from documents")
    p.add_argument("folder", nargs="?", type=Path, default=config.DOCS_DIR)
    p.add_argument("--show", type=int, default=2, help="chunks to print per file")

    i = sub.add_parser("index", help="Embed documents and store them in PostgreSQL")
    i.add_argument("folder", nargs="?", type=Path, default=config.DOCS_DIR)

    args = parser.parse_args()
    if args.command == "preview":
        preview(args.folder, args.show)
    elif args.command == "index":
        index(args.folder.resolve())


if __name__ == "__main__":
    main()

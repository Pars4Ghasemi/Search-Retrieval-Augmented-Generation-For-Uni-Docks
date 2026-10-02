# CLAUDE.md

## Working rules (from the project owner)
- **Do not do anything without consulting the user first.** Propose each step, wait for approval, then act.
- Work in phases. Report at the end of every phase and ask before starting the next one.
- Ask before every git commit and every push.
- Free and local only: no paid APIs. Keep models small.

## Project
Personal study tool: a local RAG web app to search and ask questions about university
documents (PDF, Word, PowerPoint, text/Markdown), with answers that cite their sources.

## Stack
- Python 3.12, FastAPI (backend + serves a plain HTML/JS page)
- Ollama (local): chat model `llama3.2:1b`, embedding model `nomic-embed-text`
- ChromaDB (local, stored in `data/chroma/`)
- pypdf, python-docx, python-pptx for reading files

## Layout
- `app/config.py`: settings from env / `.env`
- `app/loaders.py`: file → sections with metadata (`source`, `page` / `slide`)
- `app/chunking.py`: sections → ~800-char overlapping chunks
- `app/cli.py`: command-line tools (`preview`, later `index` / `ask`)
- `app/main.py`: FastAPI app
- `data/docs/`: user's documents (git-ignored)

## Commands
```bash
ollama serve                                  # must be running
.venv/bin/python -m app.cli preview           # check text extraction
.venv/bin/uvicorn app.main:app --reload       # run server → http://localhost:8000/health
```

## Phase plan
1. Project setup ✅
2. Document loading ✅
3. Indexing (embeddings → ChromaDB)
4. Search + answers with citations
5. Web app (upload, chat, sources)
6. Polish + push to GitHub (ask first)

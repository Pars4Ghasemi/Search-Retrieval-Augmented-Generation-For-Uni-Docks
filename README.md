# Uni Docs RAG

Ask questions about your university documents (PDF, Word, PowerPoint, text/Markdown)
and get answers with sources. Runs **100% locally and free** using [Ollama](https://ollama.com)
and ChromaDB — nothing leaves your machine.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) (`brew install ollama` on macOS)

## Setup

```bash
# 1. Start Ollama and download the models
ollama serve                       # leave running in its own terminal
ollama pull llama3.2:1b           # chat model (~1.3 GB)
ollama pull nomic-embed-text       # embedding model (~270 MB)

# 2. Create a virtual environment and install dependencies
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. (Optional) adjust settings
cp .env.example .env

# 4. Run the server
uvicorn app.main:app --reload
```

Then open http://localhost:8000/health to check everything is connected.

## Adding documents

Put your files (`.pdf`, `.docx`, `.pptx`, `.txt`, `.md`) in `data/docs/` — subfolders are fine.
To check what text gets extracted:

```bash
python -m app.cli preview
```

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `CHAT_MODEL` | `llama3.2:1b` | Ollama model that writes answers |
| `EMBED_MODEL` | `nomic-embed-text` | Ollama model used for search |
| `DOCS_DIR` | `data/docs` | Where your documents live |
| `CHROMA_DIR` | `data/chroma` | Where the search index is stored |

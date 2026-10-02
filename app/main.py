"""FastAPI entry point."""

import ollama
from fastapi import FastAPI

from app import config

app = FastAPI(title="Uni Docs RAG")


@app.get("/health")
def health():
    """Report whether Ollama is reachable and which models are installed."""
    try:
        installed = [m.model for m in ollama.Client(host=config.OLLAMA_HOST).list().models]
        ollama_ok = True
    except Exception:
        installed, ollama_ok = [], False
    return {
        "status": "ok",
        "ollama": ollama_ok,
        "chat_model": config.CHAT_MODEL,
        "embed_model": config.EMBED_MODEL,
        "installed_models": installed,
    }

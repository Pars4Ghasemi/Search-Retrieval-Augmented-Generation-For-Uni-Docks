"""App settings, read from environment variables (or a .env file)."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.2:1b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
DOCS_DIR = BASE_DIR / os.getenv("DOCS_DIR", "data/docs")
CHROMA_DIR = BASE_DIR / os.getenv("CHROMA_DIR", "data/chroma")

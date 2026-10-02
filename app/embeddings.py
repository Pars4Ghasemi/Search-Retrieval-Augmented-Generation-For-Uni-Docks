"""Turn text into vectors with a local Ollama embedding model."""

import ollama

from app import config

BATCH_SIZE = 32

# nomic-embed-text is trained with these task prefixes; they improve search quality.
_DOC_PREFIX = "search_document: "
_QUERY_PREFIX = "search_query: "


def _client() -> ollama.Client:
    return ollama.Client(host=config.OLLAMA_HOST)


def embed_documents(texts: list[str]) -> list[list[float]]:
    client = _client()
    vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = [_DOC_PREFIX + t for t in texts[i : i + BATCH_SIZE]]
        vectors.extend(client.embed(model=config.EMBED_MODEL, input=batch).embeddings)
    return vectors


def embed_query(text: str) -> list[float]:
    return _client().embed(model=config.EMBED_MODEL, input=_QUERY_PREFIX + text).embeddings[0]

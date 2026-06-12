"""Embeddings over an OpenAI-compatible HTTP endpoint.

Deliberately not an LLM SDK: provider choice stays with the user. Anything
that serves the OpenAI `/v1/embeddings` shape works — Ollama, a local LiteLLM
server, OpenRouter, OpenAI itself. Configure via env:

    EMBEDDINGS_URL      e.g. http://localhost:11434/v1   (Ollama)
    EMBEDDINGS_MODEL    e.g. nomic-embed-text
    EMBEDDINGS_API_KEY  optional, sent as a Bearer token if set
"""

from __future__ import annotations

import math

import requests

from dm_companion.config import Settings

# Wiki pages are embedded as a single vector each; longer pages are truncated.
# Plenty for campaign-wiki page sizes, and keeps us under typical model limits.
EMBED_CHAR_LIMIT = 6000

_SETUP_HINT = (
    "Semantic search is not configured. Set EMBEDDINGS_URL and EMBEDDINGS_MODEL "
    "in .env (any OpenAI-compatible endpoint works, e.g. Ollama: "
    "EMBEDDINGS_URL=http://localhost:11434/v1 EMBEDDINGS_MODEL=nomic-embed-text), "
    "then build the index with: dmc index"
)


class EmbeddingsError(RuntimeError):
    pass


class EmbeddingsClient:
    def __init__(self, base_url: str, model: str, api_key: str = ""):
        if not base_url or not model:
            raise EmbeddingsError(_SETUP_HINT)
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    @classmethod
    def from_settings(cls, settings: Settings) -> "EmbeddingsClient":
        return cls(
            settings.embeddings_url,
            settings.embeddings_model,
            settings.embeddings_api_key,
        )

    def embed(self, texts: list[str], batch_size: int = 16) -> list[list[float]]:
        """Embed texts (order-preserving). Long texts are truncated."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = [t[:EMBED_CHAR_LIMIT] for t in texts[start : start + batch_size]]
            response = requests.post(
                f"{self.base_url}/embeddings",
                json={"model": self.model, "input": batch},
                headers=headers,
                timeout=120,
            )
            if response.status_code != 200:
                raise EmbeddingsError(
                    f"Embeddings endpoint returned {response.status_code}: "
                    f"{response.text[:500]}"
                )
            data = response.json().get("data", [])
            if len(data) != len(batch):
                raise EmbeddingsError(
                    f"Embeddings endpoint returned {len(data)} vectors for "
                    f"{len(batch)} inputs"
                )
            vectors.extend(item["embedding"] for item in sorted(data, key=lambda d: d["index"]))
        return vectors


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise EmbeddingsError(
            f"Vector dimensions differ ({len(a)} vs {len(b)}) — the index was "
            "built with a different embeddings model. Rebuild with: dmc index --full"
        )
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0

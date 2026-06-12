"""Local semantic index over wiki page content.

One SQLite file, one embedding vector per page. Built/refreshed by `dmc index`
(incremental: only re-embeds pages whose content hash changed), queried by the
`find_related_lore` MCP tool with in-process cosine similarity — at campaign-
wiki scale (hundreds of pages) brute force beats running a vector database.

The index is derived data: gitignored, safe to delete, rebuilt from the wiki.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from dm_companion.embeddings import EmbeddingsClient, cosine_similarity
from dm_companion.wiki import WikiClient

_SCHEMA = """
CREATE TABLE IF NOT EXISTS pages (
    title TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    snippet TEXT NOT NULL,
    embedding TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

_WIKITEXT_NOISE = re.compile(r"\{\{[^}]*\}\}|\[\[Category:[^\]]*\]\]|<[^>]+>")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _snippet(text: str, length: int = 300) -> str:
    cleaned = _WIKITEXT_NOISE.sub(" ", text)
    return " ".join(cleaned.split())[:length]


class LoreIndex:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._db = sqlite3.connect(self.path)
        self._db.executescript(_SCHEMA)

    def get_hash(self, title: str) -> str | None:
        row = self._db.execute(
            "SELECT content_hash FROM pages WHERE title = ?", (title,)
        ).fetchone()
        return row[0] if row else None

    def upsert(self, title: str, content_hash: str, snippet: str, embedding: list[float]) -> None:
        self._db.execute(
            "INSERT INTO pages (title, content_hash, snippet, embedding, updated_at) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(title) DO UPDATE SET content_hash = excluded.content_hash, "
            "snippet = excluded.snippet, embedding = excluded.embedding, "
            "updated_at = excluded.updated_at",
            (title, content_hash, snippet, json.dumps(embedding), _now()),
        )
        self._db.commit()

    def remove_absent(self, current_titles: set[str]) -> list[str]:
        """Drop index entries for pages that no longer exist on the wiki."""
        stored = [r[0] for r in self._db.execute("SELECT title FROM pages")]
        removed = [t for t in stored if t not in current_titles]
        if removed:
            self._db.executemany("DELETE FROM pages WHERE title = ?", [(t,) for t in removed])
            self._db.commit()
        return removed

    def search(self, query_vector: list[float], limit: int = 8) -> list[dict]:
        scored = []
        for title, snippet, embedding_json in self._db.execute(
            "SELECT title, snippet, embedding FROM pages"
        ):
            score = cosine_similarity(query_vector, json.loads(embedding_json))
            scored.append({"title": title, "score": round(score, 4), "snippet": snippet})
        scored.sort(key=lambda item: -item["score"])
        return scored[:limit]

    def set_meta(self, key: str, value: str) -> None:
        self._db.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self._db.commit()

    def stats(self) -> dict:
        count = self._db.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
        meta = dict(self._db.execute("SELECT key, value FROM meta"))
        return {
            "pages": count,
            "indexed_at": meta.get("indexed_at"),
            "embeddings_model": meta.get("embeddings_model"),
        }

    def close(self) -> None:
        self._db.close()


def build_index(
    wiki: WikiClient,
    embedder: EmbeddingsClient,
    index: LoreIndex,
    full: bool = False,
    progress: Callable[[str], None] = lambda _msg: None,
) -> dict:
    """Crawl every wiki page and (re)embed the ones whose content changed.

    `full=True` re-embeds everything — needed after switching embeddings model.
    """
    titles = wiki.list_pages(limit=None)
    progress(f"Wiki has {len(titles)} pages; fetching content...")

    pending: list[tuple[str, str, str]] = []  # (title, hash, text)
    unchanged = 0
    for i, title in enumerate(titles, 1):
        page = wiki.get_page(title)
        if not page["exists"]:
            continue
        text = page["text"]
        content_hash = _content_hash(text)
        if not full and index.get_hash(title) == content_hash:
            unchanged += 1
            continue
        pending.append((title, content_hash, text))
        if i % 50 == 0:
            progress(f"  fetched {i}/{len(titles)} pages...")

    progress(f"Embedding {len(pending)} new/changed pages ({unchanged} unchanged)...")
    batch_size = 16
    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        # Title is prepended so the page name itself carries semantic weight.
        vectors = embedder.embed([f"{title}\n\n{text}" for title, _h, text in batch])
        for (title, content_hash, text), vector in zip(batch, vectors):
            index.upsert(title, content_hash, _snippet(text), vector)
        progress(f"  embedded {min(start + batch_size, len(pending))}/{len(pending)}")

    removed = index.remove_absent(set(titles))
    index.set_meta("indexed_at", _now())
    index.set_meta("embeddings_model", embedder.model)
    return {
        "total_pages": len(titles),
        "embedded": len(pending),
        "unchanged": unchanged,
        "removed": removed,
    }

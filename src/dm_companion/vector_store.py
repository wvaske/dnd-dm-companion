"""Pluggable vector storage for semantic lore search.

Two backends behind the same interface, chosen by VECTOR_BACKEND:

- SqliteVectorStore (default): one local file, in-process cosine similarity.
  Right answer for a campaign wiki (hundreds of pages) with zero infrastructure.
- OpenSearchVectorStore: k-NN index over plain REST (no SDK). Use when the
  corpus grows past brute force — e.g. full sourcebooks ingested as thousands
  of chunks. Works against the OpenSearch instance already backing CirrusSearch.

Documents carry a stable doc_id (namespaced by prefix) and a source tag:

    doc_id "wiki::<title>"          source "wiki" or "wiki:<Namespace>"
    doc_id "book::<slug>::<seq>"    source "book:<slug>"

Search scopes build on the source tag: "campaign" is the wiki main namespace
(source == "wiki"); "official" is everything else — ingested sourcebooks and
any extra wiki namespaces (reference material); "all" is both.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

from dm_companion.config import Settings
from dm_companion.embeddings import cosine_similarity

SCOPES = ("all", "campaign", "official")


class VectorStoreError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _check_scope(scope: str) -> None:
    if scope not in SCOPES:
        raise VectorStoreError(f"Unknown scope {scope!r}; expected one of {SCOPES}.")


def _matches_scope(source: str, scope: str) -> bool:
    if scope == "campaign":
        return source == "wiki"
    if scope == "official":
        return source != "wiki"
    return True


def open_vector_store(settings: Settings):
    """Factory: the backend is configuration, callers never branch on it."""
    backend = settings.vector_backend or "sqlite"
    if backend == "sqlite":
        return SqliteVectorStore(settings.index_path)
    if backend == "opensearch":
        if not settings.opensearch_url:
            raise VectorStoreError(
                "VECTOR_BACKEND=opensearch requires OPENSEARCH_URL (e.g. "
                "http://localhost:9200) in .env."
            )
        return OpenSearchVectorStore(
            settings.opensearch_url,
            index=settings.opensearch_index,
            username=settings.opensearch_username,
            password=settings.opensearch_password,
        )
    raise VectorStoreError(
        f"Unknown VECTOR_BACKEND {backend!r}; expected 'sqlite' or 'opensearch'."
    )


# --------------------------------------------------------------------- sqlite

_SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    doc_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
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


class SqliteVectorStore:
    backend = "sqlite"

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._db = sqlite3.connect(self.path)
        # Pre-sourcebook versions used a `pages` table; it's derived data,
        # so migrate by dropping (a `dmc index` run repopulates).
        self._db.execute("DROP TABLE IF EXISTS pages")
        self._db.executescript(_SQLITE_SCHEMA)

    def get_hash(self, doc_id: str) -> str | None:
        row = self._db.execute(
            "SELECT content_hash FROM documents WHERE doc_id = ?", (doc_id,)
        ).fetchone()
        return row[0] if row else None

    def upsert(
        self,
        doc_id: str,
        source: str,
        title: str,
        content_hash: str,
        snippet: str,
        embedding: list[float],
    ) -> None:
        self._db.execute(
            "INSERT INTO documents (doc_id, source, title, content_hash, snippet, "
            "embedding, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(doc_id) DO UPDATE SET source = excluded.source, "
            "title = excluded.title, content_hash = excluded.content_hash, "
            "snippet = excluded.snippet, embedding = excluded.embedding, "
            "updated_at = excluded.updated_at",
            (doc_id, source, title, content_hash, snippet, json.dumps(embedding), _now()),
        )
        self._db.commit()

    def remove_absent(self, prefix: str, current_ids: set[str]) -> list[str]:
        """Drop documents under a doc_id prefix that are no longer current."""
        stored = [
            r[0]
            for r in self._db.execute(
                "SELECT doc_id FROM documents WHERE doc_id LIKE ?", (prefix + "%",)
            )
        ]
        removed = [d for d in stored if d not in current_ids]
        if removed:
            self._db.executemany(
                "DELETE FROM documents WHERE doc_id = ?", [(d,) for d in removed]
            )
            self._db.commit()
        return removed

    def delete_by_prefix(self, prefix: str) -> int:
        cursor = self._db.execute(
            "DELETE FROM documents WHERE doc_id LIKE ?", (prefix + "%",)
        )
        self._db.commit()
        return cursor.rowcount

    def search(self, query_vector: list[float], limit: int = 8, scope: str = "all") -> list[dict]:
        _check_scope(scope)
        scored = []
        for source, title, snippet, embedding_json in self._db.execute(
            "SELECT source, title, snippet, embedding FROM documents"
        ):
            if not _matches_scope(source, scope):
                continue
            score = cosine_similarity(query_vector, json.loads(embedding_json))
            scored.append(
                {"title": title, "score": round(score, 4), "snippet": snippet, "source": source}
            )
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
        sources = dict(
            self._db.execute("SELECT source, COUNT(*) FROM documents GROUP BY source")
        )
        meta = dict(self._db.execute("SELECT key, value FROM meta"))
        return {
            "backend": self.backend,
            "documents": sum(sources.values()),
            "sources": sources,
            "indexed_at": meta.get("indexed_at"),
            "embeddings_model": meta.get("embeddings_model"),
        }

    def close(self) -> None:
        self._db.close()


# ----------------------------------------------------------------- opensearch


class OpenSearchVectorStore:
    """k-NN storage on OpenSearch, REST only.

    The index is created lazily on first upsert (the embedding dimension isn't
    known until then). Scoped searches over-fetch (k = limit * 4) and filter
    client-side, which works on any OpenSearch version including the 1.x line
    that predates efficient k-NN filtering.
    """

    backend = "opensearch"

    def __init__(self, url: str, index: str = "dmc-lore", username: str = "", password: str = ""):
        self.base_url = url.rstrip("/")
        self.index = index
        self.meta_index = f"{index}-meta"
        self.auth = (username, password) if username else None

    def _request(self, method: str, path: str, body: dict | None = None, ok_404: bool = False):
        response = requests.request(
            method, f"{self.base_url}{path}", json=body, auth=self.auth, timeout=60
        )
        if response.status_code == 404 and ok_404:
            return None
        if response.status_code >= 400:
            raise VectorStoreError(
                f"OpenSearch {method} {path} failed ({response.status_code}): "
                f"{response.text[:500]}"
            )
        return response.json() if response.content else {}

    def _ensure_index(self, dimension: int) -> None:
        if self._request("GET", f"/{self.index}", ok_404=True) is not None:
            return
        self._request(
            "PUT",
            f"/{self.index}",
            {
                "settings": {"index": {"knn": True}},
                "mappings": {
                    "properties": {
                        "doc_id": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "title": {"type": "text"},
                        "content_hash": {"type": "keyword"},
                        "snippet": {"type": "text"},
                        "embedding": {"type": "knn_vector", "dimension": dimension},
                        "updated_at": {"type": "keyword"},
                    }
                },
            },
        )

    def get_hash(self, doc_id: str) -> str | None:
        doc = self._request("GET", f"/{self.index}/_doc/{quote(doc_id, safe='')}", ok_404=True)
        return doc["_source"].get("content_hash") if doc else None

    def upsert(
        self,
        doc_id: str,
        source: str,
        title: str,
        content_hash: str,
        snippet: str,
        embedding: list[float],
    ) -> None:
        self._ensure_index(len(embedding))
        self._request(
            "PUT",
            f"/{self.index}/_doc/{quote(doc_id, safe='')}",
            {
                "doc_id": doc_id,
                "source": source,
                "title": title,
                "content_hash": content_hash,
                "snippet": snippet,
                "embedding": embedding,
                "updated_at": _now(),
            },
        )

    def _all_ids_with_prefix(self, prefix: str) -> list[str]:
        self._request("POST", f"/{self.index}/_refresh", ok_404=True)
        result = self._request(
            "POST",
            f"/{self.index}/_search",
            {
                "size": 10000,
                "_source": ["doc_id"],
                "query": {"prefix": {"doc_id": prefix}},
            },
            ok_404=True,
        )
        if result is None:
            return []
        return [hit["_source"]["doc_id"] for hit in result["hits"]["hits"]]

    def remove_absent(self, prefix: str, current_ids: set[str]) -> list[str]:
        removed = [d for d in self._all_ids_with_prefix(prefix) if d not in current_ids]
        for doc_id in removed:
            self._request("DELETE", f"/{self.index}/_doc/{quote(doc_id, safe='')}", ok_404=True)
        return removed

    def delete_by_prefix(self, prefix: str) -> int:
        self._request("POST", f"/{self.index}/_refresh", ok_404=True)
        result = self._request(
            "POST",
            f"/{self.index}/_delete_by_query",
            {"query": {"prefix": {"doc_id": prefix}}},
            ok_404=True,
        )
        return result.get("deleted", 0) if result else 0

    def search(self, query_vector: list[float], limit: int = 8, scope: str = "all") -> list[dict]:
        _check_scope(scope)
        self._request("POST", f"/{self.index}/_refresh", ok_404=True)
        k = limit if scope == "all" else limit * 4
        result = self._request(
            "POST",
            f"/{self.index}/_search",
            {
                "size": k,
                "_source": ["source", "title", "snippet"],
                "query": {"knn": {"embedding": {"vector": query_vector, "k": k}}},
            },
            ok_404=True,
        )
        if result is None:
            return []
        matches = []
        for hit in result["hits"]["hits"]:
            doc = hit["_source"]
            if not _matches_scope(doc["source"], scope):
                continue
            matches.append(
                {
                    "title": doc["title"],
                    "score": round(hit["_score"], 4),
                    "snippet": doc["snippet"],
                    "source": doc["source"],
                }
            )
        return matches[:limit]

    def set_meta(self, key: str, value: str) -> None:
        self._request(
            "POST",
            f"/{self.meta_index}/_update/meta",
            {"doc": {key: value}, "doc_as_upsert": True},
        )

    def stats(self) -> dict:
        self._request("POST", f"/{self.index}/_refresh", ok_404=True)
        result = self._request(
            "POST",
            f"/{self.index}/_search",
            {"size": 0, "aggs": {"sources": {"terms": {"field": "source", "size": 100}}}},
            ok_404=True,
        )
        sources = {}
        if result:
            for bucket in result["aggregations"]["sources"]["buckets"]:
                sources[bucket["key"]] = bucket["doc_count"]
        meta_doc = self._request("GET", f"/{self.meta_index}/_doc/meta", ok_404=True)
        meta = meta_doc["_source"] if meta_doc else {}
        return {
            "backend": self.backend,
            "documents": sum(sources.values()),
            "sources": sources,
            "indexed_at": meta.get("indexed_at"),
            "embeddings_model": meta.get("embeddings_model"),
        }

    def close(self) -> None:
        pass

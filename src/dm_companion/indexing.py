"""Builds the semantic lore index from two kinds of corpus.

- sync_wiki: every wiki page becomes one document (incremental by content
  hash). Main-namespace pages are campaign lore (source "wiki"); extra
  configured namespaces — e.g. a DM-only Sourcebook: namespace — are tagged
  "wiki:<Namespace>" and count as reference material in scoped searches.
- ingest_book: a markdown/plain-text sourcebook is chunked by headings and
  stored under source "book:<slug>", no wiki involvement. This is the direct
  path for official material too big or too licensed to paste into the wiki.

Both run through `dmc` (deterministic side); judgment about *using* the
results lives in skills (find_related_lore, canon-check).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from dm_companion.embeddings import EmbeddingsClient
from dm_companion.wiki import WikiClient

EMBED_BATCH = 16
CHUNK_CHARS = 4000
BOOK_EXTENSIONS = (".md", ".markdown", ".txt")

_WIKITEXT_NOISE = re.compile(r"\{\{[^}]*\}\}|\[\[Category:[^\]]*\]\]|<[^>]+>")
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


class IndexingError(RuntimeError):
    pass


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _snippet(text: str, length: int = 300) -> str:
    cleaned = _WIKITEXT_NOISE.sub(" ", text)
    return " ".join(cleaned.split())[:length]


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        raise IndexingError(f"Cannot derive a source slug from {name!r}.")
    return slug


# ----------------------------------------------------------------- wiki sync


def sync_wiki(
    wiki: WikiClient,
    embedder: EmbeddingsClient,
    store,
    namespaces: tuple[int, ...] = (0,),
    full: bool = False,
    progress: Callable[[str], None] = lambda _msg: None,
) -> dict:
    """(Re)embed wiki pages whose content changed; prune deleted pages.

    `full=True` re-embeds everything — needed after switching embeddings model.
    """
    pending: list[tuple[str, str, str, str, str]] = []  # doc_id, source, title, hash, text
    current_ids: set[str] = set()
    unchanged = 0

    for namespace in namespaces:
        titles = wiki.list_pages(limit=None, namespace=namespace)
        progress(f"Namespace {namespace}: {len(titles)} pages; fetching content...")
        for i, title in enumerate(titles, 1):
            page = wiki.get_page(title)
            if not page["exists"]:
                continue
            doc_id = f"wiki::{title}"
            current_ids.add(doc_id)
            if namespace == 0 or ":" not in title:
                source = "wiki"
            else:
                source = f"wiki:{title.split(':', 1)[0]}"
            text = page["text"]
            content_hash = _content_hash(text)
            if not full and store.get_hash(doc_id) == content_hash:
                unchanged += 1
                continue
            pending.append((doc_id, source, title, content_hash, text))
            if i % 50 == 0:
                progress(f"  fetched {i}/{len(titles)} pages...")

    progress(f"Embedding {len(pending)} new/changed pages ({unchanged} unchanged)...")
    for start in range(0, len(pending), EMBED_BATCH):
        batch = pending[start : start + EMBED_BATCH]
        # Title is prepended so the page name itself carries semantic weight.
        vectors = embedder.embed([f"{title}\n\n{text}" for _d, _s, title, _h, text in batch])
        for (doc_id, source, title, content_hash, text), vector in zip(batch, vectors):
            store.upsert(doc_id, source, title, content_hash, _snippet(text), vector)
        progress(f"  embedded {min(start + EMBED_BATCH, len(pending))}/{len(pending)}")

    removed = store.remove_absent("wiki::", current_ids)
    store.set_meta("indexed_at", _now_meta())
    store.set_meta("embeddings_model", embedder.model)
    return {
        "total_pages": len(current_ids),
        "embedded": len(pending),
        "unchanged": unchanged,
        "removed": removed,
    }


def _now_meta() -> str:
    from dm_companion.vector_store import _now

    return _now()


# ------------------------------------------------------------------- books


@dataclass
class Chunk:
    heading: str  # breadcrumb of markdown headings, e.g. "Chapter 3 > Elves"
    text: str


def chunk_markdown(text: str, max_chars: int = CHUNK_CHARS) -> list[Chunk]:
    """Split markdown (or plain text) into heading-scoped chunks.

    Heading breadcrumbs keep retrieval results legible ("PHB — Chapter 9 >
    Combat > Cover"); sections longer than max_chars are split, repeating the
    breadcrumb. Plain text without headings degrades to fixed-size chunks.
    """
    chunks: list[Chunk] = []
    stack: list[tuple[int, str]] = []  # (heading level, heading text)
    buffer: list[str] = []
    buffered = 0

    def flush() -> None:
        nonlocal buffered
        body = "\n".join(buffer).strip()
        buffer.clear()
        buffered = 0
        if not body:
            return
        heading = " > ".join(h for _level, h in stack) or "(beginning)"
        for start in range(0, len(body), max_chars):
            chunks.append(Chunk(heading=heading, text=body[start : start + max_chars]))

    for line in text.splitlines():
        match = _HEADING.match(line)
        if match:
            flush()
            level = len(match.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, match.group(2)))
        else:
            buffer.append(line)
            buffered += len(line) + 1
            if buffered > max_chars:
                flush()
    flush()
    return chunks


def ingest_book(
    path: str | Path,
    title: str,
    embedder: EmbeddingsClient,
    store,
    full: bool = False,
    progress: Callable[[str], None] = lambda _msg: None,
) -> dict:
    """Chunk, embed, and store a sourcebook file under source "book:<slug>".

    Re-ingesting the same title replaces its chunks (unchanged chunks are
    skipped by content hash, stale ones pruned), so an updated export of the
    same book is a cheap re-run.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise IndexingError(f"File not found: {path}")
    if file_path.suffix.lower() not in BOOK_EXTENSIONS:
        raise IndexingError(
            f"Unsupported file type {file_path.suffix!r}; expected one of "
            f"{BOOK_EXTENSIONS}. Convert PDFs first (e.g. `pdftotext -layout` "
            "or pandoc) — text quality in beats text quality out."
        )

    chunks = chunk_markdown(file_path.read_text(encoding="utf-8", errors="replace"))
    if not chunks:
        raise IndexingError(f"No content found in {path}.")

    slug = slugify(title)
    source = f"book:{slug}"
    prefix = f"book::{slug}::"
    progress(f"{title}: {len(chunks)} chunks from {file_path.name}")

    pending: list[tuple[str, str, Chunk]] = []  # doc_id, hash, chunk
    current_ids: set[str] = set()
    unchanged = 0
    for seq, chunk in enumerate(chunks):
        doc_id = f"{prefix}{seq:05d}"
        current_ids.add(doc_id)
        content_hash = _content_hash(chunk.heading + "\n" + chunk.text)
        if not full and store.get_hash(doc_id) == content_hash:
            unchanged += 1
            continue
        pending.append((doc_id, content_hash, chunk))

    progress(f"Embedding {len(pending)} new/changed chunks ({unchanged} unchanged)...")
    for start in range(0, len(pending), EMBED_BATCH):
        batch = pending[start : start + EMBED_BATCH]
        vectors = embedder.embed(
            [f"{title} — {chunk.heading}\n\n{chunk.text}" for _d, _h, chunk in batch]
        )
        for (doc_id, content_hash, chunk), vector in zip(batch, vectors):
            store.upsert(
                doc_id,
                source,
                f"{title} — {chunk.heading}",
                content_hash,
                _snippet(chunk.text),
                vector,
            )
        progress(f"  embedded {min(start + EMBED_BATCH, len(pending))}/{len(pending)}")

    removed = store.remove_absent(prefix, current_ids)
    store.set_meta("indexed_at", _now_meta())
    store.set_meta("embeddings_model", embedder.model)
    return {
        "source": source,
        "chunks": len(chunks),
        "embedded": len(pending),
        "unchanged": unchanged,
        "removed": removed,
    }

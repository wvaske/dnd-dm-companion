"""Command-line entry points (the deterministic half of the companion).

Skills call these for steps that should never be left to LLM improvisation:
transcript conversion, connectivity checks. Usage:

    dmc transcript path/to/zoom.vtt -o sessions/session-25.md
    dmc check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dm_companion.transcripts import merge_utterances, parse_vtt, to_markdown


def cmd_transcript(args: argparse.Namespace) -> int:
    path = Path(args.vtt_file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    utterances = parse_vtt(path)
    if not utterances:
        print(f"error: no cues parsed from {path} — is it a WebVTT file?", file=sys.stderr)
        return 1
    merged = merge_utterances(utterances, max_gap=args.merge_gap)
    markdown = to_markdown(merged, title=args.title or f"Session Transcript: {path.stem}")

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown, encoding="utf-8")
        print(f"Wrote {len(merged)} utterances ({len(utterances)} raw cues) to {out}")
    else:
        print(markdown)
    return 0


def _open_semantic_stack():
    """Settings + embedder + vector store, with friendly config errors."""
    from dm_companion.embeddings import EmbeddingsClient
    from dm_companion.vector_store import open_vector_store
    from dm_companion.wiki import WikiClient

    wiki = WikiClient()
    embedder = EmbeddingsClient.from_settings(wiki.settings)
    store = open_vector_store(wiki.settings)
    return wiki, embedder, store


def cmd_index(args: argparse.Namespace) -> int:
    from dm_companion.embeddings import EmbeddingsError
    from dm_companion.indexing import sync_wiki
    from dm_companion.vector_store import VectorStoreError

    try:
        wiki, embedder, store = _open_semantic_stack()
    except (EmbeddingsError, VectorStoreError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    namespaces = (
        tuple(int(ns) for ns in args.namespaces.split(","))
        if args.namespaces
        else wiki.settings.index_namespaces
    )
    try:
        summary = sync_wiki(
            wiki, embedder, store, namespaces=namespaces, full=args.full, progress=print
        )
    finally:
        store.close()
    print(
        f"Done: {summary['embedded']} embedded, {summary['unchanged']} unchanged, "
        f"{len(summary['removed'])} removed (wiki has {summary['total_pages']} pages)"
    )
    for doc_id in summary["removed"]:
        print(f"  removed from index: {doc_id}")
    return 0


def cmd_ingest_book(args: argparse.Namespace) -> int:
    from dm_companion.embeddings import EmbeddingsError
    from dm_companion.indexing import IndexingError, ingest_book
    from dm_companion.vector_store import VectorStoreError

    try:
        _wiki, embedder, store = _open_semantic_stack()
    except (EmbeddingsError, VectorStoreError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        summary = ingest_book(
            args.file, title=args.title, embedder=embedder, store=store,
            full=args.full, progress=print,
        )
    except IndexingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        store.close()
    print(
        f"Done: {summary['source']} — {summary['chunks']} chunks "
        f"({summary['embedded']} embedded, {summary['unchanged']} unchanged, "
        f"{len(summary['removed'])} stale removed)"
    )
    return 0


def cmd_remove_book(args: argparse.Namespace) -> int:
    from dm_companion.indexing import slugify
    from dm_companion.vector_store import VectorStoreError, open_vector_store
    from dm_companion.wiki import WikiClient

    try:
        store = open_vector_store(WikiClient().settings)
    except VectorStoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    try:
        deleted = store.delete_by_prefix(f"book::{slugify(args.title)}::")
    finally:
        store.close()
    print(f"Removed {deleted} chunks for {args.title!r}")
    return 0


def cmd_check(_args: argparse.Namespace) -> int:
    from dm_companion.vector_store import open_vector_store
    from dm_companion.wiki import WikiClient

    client = WikiClient()
    settings = client.settings
    print(f"Wiki:      {settings.wiki_url}")
    print(f"Bot user:  {settings.bot_username or '(anonymous)'}")
    print(f"Read-only: {settings.read_only}")
    if settings.embeddings_url:
        store = open_vector_store(settings)
        try:
            stats = store.stats()
        finally:
            store.close()
        print(
            f"Semantic:  {settings.embeddings_url} ({settings.embeddings_model}) "
            f"-> {stats['backend']} backend, {stats['documents']} documents"
            + (f", built {stats['indexed_at']}" if stats["indexed_at"] else " — run: dmc index")
        )
        for source, count in sorted(stats["sources"].items()):
            print(f"             {source}: {count}")
    else:
        print("Semantic:  not configured (set EMBEDDINGS_URL / EMBEDDINGS_MODEL to enable)")
    try:
        results = client.search("a", limit=1)
    except Exception as exc:  # surface the real error, whatever mwclient raises
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"OK: connected and search works ({len(results)} result returned)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dmc", description="D&D DM companion CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_transcript = sub.add_parser(
        "transcript", help="Convert a Zoom .vtt transcript to clean markdown"
    )
    p_transcript.add_argument("vtt_file", help="Path to the Zoom WebVTT transcript")
    p_transcript.add_argument("-o", "--output", help="Output markdown file (default: stdout)")
    p_transcript.add_argument("--title", help="Document title")
    p_transcript.add_argument(
        "--merge-gap",
        type=float,
        default=30.0,
        help="Merge same-speaker cues separated by at most this many seconds (default: 30)",
    )
    p_transcript.set_defaults(func=cmd_transcript)

    p_index = sub.add_parser(
        "index", help="Sync wiki pages into the semantic lore index (incremental)"
    )
    p_index.add_argument(
        "--full",
        action="store_true",
        help="Re-embed every page (required after changing EMBEDDINGS_MODEL)",
    )
    p_index.add_argument(
        "--namespaces",
        help='Wiki namespace ids to index, e.g. "0,3000" (default: $INDEX_NAMESPACES or 0)',
    )
    p_index.set_defaults(func=cmd_index)

    p_book = sub.add_parser(
        "ingest-book",
        help="Add a sourcebook (.md/.txt) to the lore index as official reference material",
    )
    p_book.add_argument("file", help="Markdown or plain-text export of the book")
    p_book.add_argument(
        "--title", required=True, help='Book title, e.g. "Player\'s Handbook"'
    )
    p_book.add_argument(
        "--full", action="store_true", help="Re-embed all chunks even if unchanged"
    )
    p_book.set_defaults(func=cmd_ingest_book)

    p_rm_book = sub.add_parser(
        "remove-book", help="Remove an ingested sourcebook from the lore index"
    )
    p_rm_book.add_argument("title", help="The title used at ingest time")
    p_rm_book.set_defaults(func=cmd_remove_book)

    p_check = sub.add_parser("check", help="Verify wiki connectivity and credentials")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

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


def cmd_check(_args: argparse.Namespace) -> int:
    from dm_companion.wiki import WikiClient

    client = WikiClient()
    settings = client.settings
    print(f"Wiki:      {settings.wiki_url}")
    print(f"Bot user:  {settings.bot_username or '(anonymous)'}")
    print(f"Read-only: {settings.read_only}")
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

    p_check = sub.add_parser("check", help="Verify wiki connectivity and credentials")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

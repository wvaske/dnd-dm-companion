"""Zoom WebVTT transcript parsing.

Zoom cloud-recording transcripts are WebVTT files where each cue's text is
prefixed with the Zoom display name of the *account* that was speaking:

    WEBVTT

    1
    00:00:03.600 --> 00:00:06.300
    Wes Vaske: Alright, last time you were in Waterdeep...

Important: the Zoom display name identifies a *microphone*, not a person.
Colocated players share one account, so a speaker label like "Wes Vaske" may
cover the DM plus two players. This module is deliberately deterministic — it
parses, merges, and formats. Attributing utterances to actual people/characters
is a judgment call left to the ingest-session skill (an LLM with the campaign
roster and context).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from pathlib import Path

_TIMESTAMP_RE = re.compile(
    r"(?:(\d+):)?(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(?:(\d+):)?(\d{2}):(\d{2})[.,](\d{3})"
)
# Zoom speaker prefix: "Display Name: text". Display names can contain spaces,
# digits, parens, etc., but not a colon; require the colon-space delimiter.
_SPEAKER_RE = re.compile(r"^([^:\n]{1,80}?):\s+(.*)$", re.DOTALL)


@dataclass
class Utterance:
    speaker: str  # Zoom display name ("?" when the cue had no speaker prefix)
    start: float  # seconds from recording start
    end: float
    text: str


def _ts_to_seconds(h: str | None, m: str, s: str, ms: str) -> float:
    return int(h or 0) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"


def parse_vtt(source: str | Path) -> list[Utterance]:
    """Parse a WebVTT file (or its content as a string) into utterances."""
    if isinstance(source, Path):
        content = source.read_text(encoding="utf-8-sig")
    elif "\n" not in source and Path(source).exists():
        content = Path(source).read_text(encoding="utf-8-sig")
    else:
        content = source

    utterances: list[Utterance] = []
    blocks = re.split(r"\n\s*\n", content.strip())
    for block in blocks:
        lines = [ln.strip() for ln in block.strip().splitlines()]
        if not lines or lines[0].startswith(("WEBVTT", "NOTE", "STYLE")):
            continue

        match = None
        text_start = 0
        for i, line in enumerate(lines):
            match = _TIMESTAMP_RE.search(line)
            if match:
                text_start = i + 1
                break
        if not match:
            continue

        start = _ts_to_seconds(*match.groups()[:4])
        end = _ts_to_seconds(*match.groups()[4:])
        text = " ".join(lines[text_start:]).strip()
        if not text:
            continue

        speaker_match = _SPEAKER_RE.match(text)
        if speaker_match:
            speaker, text = speaker_match.group(1).strip(), speaker_match.group(2).strip()
        else:
            speaker = "?"
        utterances.append(Utterance(speaker=speaker, start=start, end=end, text=text))
    return utterances


def merge_utterances(utterances: list[Utterance], max_gap: float = 30.0) -> list[Utterance]:
    """Merge consecutive cues from the same speaker into readable paragraphs.

    Zoom emits a cue every few seconds, which is unreadable raw. Cues merge
    when the speaker is unchanged and the silence between cues is <= max_gap
    seconds; a longer pause starts a new utterance even for the same speaker.
    """
    merged: list[Utterance] = []
    for utt in utterances:
        if (
            merged
            and merged[-1].speaker == utt.speaker
            and utt.start - merged[-1].end <= max_gap
        ):
            prev = merged[-1]
            merged[-1] = replace(prev, end=utt.end, text=prev.text + " " + utt.text)
        else:
            merged.append(replace(utt))
    return merged


def speaker_stats(utterances: list[Utterance]) -> dict[str, dict]:
    stats: dict[str, dict] = {}
    for utt in utterances:
        entry = stats.setdefault(utt.speaker, {"utterances": 0, "talk_seconds": 0.0})
        entry["utterances"] += 1
        entry["talk_seconds"] += utt.end - utt.start
    return stats


def to_markdown(utterances: list[Utterance], title: str = "Session Transcript") -> str:
    """Render merged utterances as markdown for skill/LLM consumption."""
    lines = [f"# {title}", ""]
    if utterances:
        duration = format_timestamp(max(u.end for u in utterances))
        lines.append(f"- **Duration:** {duration}")
        lines.append("- **Zoom accounts heard** (one account may cover multiple colocated people):")
        for speaker, st in sorted(
            speaker_stats(utterances).items(), key=lambda kv: -kv[1]["talk_seconds"]
        ):
            talk = format_timestamp(st["talk_seconds"])
            lines.append(f"  - {speaker}: {st['utterances']} utterances, {talk} talk time")
        lines.append("")
        lines.append("---")
        lines.append("")
    for utt in utterances:
        lines.append(f"**[{format_timestamp(utt.start)}] {utt.speaker}:** {utt.text}")
        lines.append("")
    return "\n".join(lines)

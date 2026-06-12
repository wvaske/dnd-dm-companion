from pathlib import Path

import pytest

from dm_companion.transcripts import merge_utterances, parse_vtt, to_markdown
from dm_companion.transcripts.vtt import format_timestamp, speaker_stats

FIXTURE = Path(__file__).parent / "fixtures" / "sample.vtt"


@pytest.fixture
def utterances():
    return parse_vtt(FIXTURE)


def test_parse_cue_count(utterances):
    assert len(utterances) == 7


def test_speaker_extraction(utterances):
    assert utterances[0].speaker == "Wes Vaske"
    assert utterances[2].speaker == "Bob Smith"


def test_timestamps(utterances):
    assert utterances[0].start == pytest.approx(3.6)
    assert utterances[0].end == pytest.approx(6.3)


def test_text_without_speaker_prefix(utterances):
    assert utterances[0].text == "Alright, last time you were in Waterdeep."


def test_unattributed_cue_marked_unknown(utterances):
    assert utterances[-1].speaker == "?"


def test_merge_same_speaker_within_gap(utterances):
    merged = merge_utterances(utterances, max_gap=30.0)
    # Cues 1+2 (Wes, 0.5s gap) merge; cue 4 (Wes) doesn't merge into 1+2
    # because Bob speaks in between; cue 5 (Wes, 46s after cue 4) exceeds
    # default-irrelevant gap only when max_gap < 46.
    assert merged[0].speaker == "Wes Vaske"
    assert "Waterdeep" in merged[0].text and "Yawning Portal" in merged[0].text
    assert merged[0].end == pytest.approx(10.1)


def test_merge_respects_max_gap(utterances):
    tight = merge_utterances(utterances, max_gap=5.0)
    loose = merge_utterances(utterances, max_gap=120.0)
    assert len(tight) >= len(loose)
    # With a huge gap allowance, cue 4 and cue 5 (both Wes) still must not
    # merge across Bob's interjection.
    speakers = [u.speaker for u in loose]
    assert speakers == ["Wes Vaske", "Bob Smith", "Wes Vaske", "Bob Smith", "?"]


def test_markdown_output(utterances):
    md = to_markdown(merge_utterances(utterances), title="Test Session")
    assert md.startswith("# Test Session")
    assert "**[0:00:03] Wes Vaske:**" in md
    assert "colocated" in md  # the shared-mic warning is present


def test_speaker_stats(utterances):
    stats = speaker_stats(utterances)
    assert stats["Wes Vaske"]["utterances"] == 4
    assert stats["Bob Smith"]["utterances"] == 2


def test_format_timestamp():
    assert format_timestamp(3.6) == "0:00:03"
    assert format_timestamp(3725) == "1:02:05"


def test_parse_from_string():
    content = FIXTURE.read_text()
    assert len(parse_vtt(content)) == 7

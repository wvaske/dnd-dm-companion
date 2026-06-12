"""Safety-rail tests for WikiClient writes.

These cover the validation that must happen *before* any network call, so a
real wiki is never needed. A client whose checks pass would try to connect —
tests are arranged so the guard under test always trips first.
"""

import pytest

from dm_companion.config import Settings
from dm_companion.wiki import WikiClient, WikiError


def make_client(read_only=False):
    return WikiClient(
        Settings(
            wiki_url="https://wiki.example.invalid",
            bot_username="",
            bot_password="",
            read_only=read_only,
        )
    )


def test_save_blocked_in_read_only_mode():
    with pytest.raises(WikiError, match="read-only"):
        make_client(read_only=True).save_page("T", "text", summary="s")


def test_save_requires_edit_summary():
    with pytest.raises(WikiError, match="summary"):
        make_client().save_page("T", "text", summary="   ")


def test_save_rejects_unknown_mode():
    with pytest.raises(WikiError, match="mode"):
        make_client().save_page("T", "text", summary="s", mode="overwrite")


def test_upload_blocked_in_read_only_mode(tmp_path):
    image = tmp_path / "map.png"
    image.write_bytes(b"\x89PNG")
    with pytest.raises(WikiError, match="read-only"):
        make_client(read_only=True).upload_image(str(image), summary="s")


def test_upload_requires_summary(tmp_path):
    image = tmp_path / "map.png"
    image.write_bytes(b"\x89PNG")
    with pytest.raises(WikiError, match="summary"):
        make_client().upload_image(str(image), summary="")


def test_upload_rejects_missing_file():
    with pytest.raises(WikiError, match="not found"):
        make_client().upload_image("/nonexistent/map.png", summary="s")


def test_upload_rejects_non_image_extension(tmp_path):
    sneaky = tmp_path / "payload.php"
    sneaky.write_text("<?php")
    with pytest.raises(WikiError, match="Unsupported file type"):
        make_client().upload_image(str(sneaky), summary="s")

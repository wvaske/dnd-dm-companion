"""Safety-rail tests for WikiClient writes.

These cover the validation that must happen *before* any network call, so a
real wiki is never needed. A client whose checks pass would try to connect —
tests are arranged so the guard under test always trips first.
"""

import mwclient.errors
import pytest

from dm_companion.config import Settings
from dm_companion.wiki import WikiClient, WikiError


def make_client(read_only=False, bot_username=""):
    return WikiClient(
        Settings(
            wiki_url="https://wiki.example.invalid",
            bot_username=bot_username,
            bot_password="pw" if bot_username else "",
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


# --- re-login on expired bot session (no network: stubbed action + _login) ---


def test_write_retries_once_after_session_expiry(monkeypatch):
    """An expired session (AssertUserFailedError) triggers a re-login + one retry."""
    client = make_client(bot_username="bot@example")
    client._site = object()  # non-None so the `site` property skips real network setup

    relogins = []
    monkeypatch.setattr(client, "_login", lambda site: relogins.append(site))

    attempts = {"n": 0}

    def action():
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise mwclient.errors.AssertUserFailedError()
        return "saved"

    assert client._write_with_relogin(action) == "saved"
    assert attempts["n"] == 2  # failed once, retried once
    assert len(relogins) == 1  # re-authenticated exactly once


def test_write_does_not_retry_without_credentials(monkeypatch):
    """With no bot credentials there is nothing to recover with — surface honestly."""
    client = make_client(bot_username="")
    client._site = object()
    monkeypatch.setattr(
        client, "_login", lambda site: pytest.fail("must not re-login without credentials")
    )

    attempts = {"n": 0}

    def action():
        attempts["n"] += 1
        raise mwclient.errors.AssertUserFailedError()

    with pytest.raises(mwclient.errors.AssertUserFailedError):
        client._write_with_relogin(action)
    assert attempts["n"] == 1  # no retry


def test_write_propagates_other_errors_without_retry(monkeypatch):
    """Errors other than an expired session are not retried."""
    client = make_client(bot_username="bot@example")
    client._site = object()
    monkeypatch.setattr(
        client, "_login", lambda site: pytest.fail("must not re-login on unrelated errors")
    )

    attempts = {"n": 0}

    def action():
        attempts["n"] += 1
        raise mwclient.errors.ProtectedPageError("page is protected")

    with pytest.raises(mwclient.errors.ProtectedPageError):
        client._write_with_relogin(action)
    assert attempts["n"] == 1

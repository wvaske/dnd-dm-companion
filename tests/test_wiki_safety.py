"""Safety-rail tests for WikiClient writes.

These cover the validation that must happen *before* any network call, so a
real wiki is never needed. A client whose checks pass would try to connect —
tests are arranged so the guard under test always trips first.
"""

import time

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
    client._session_checked_at = time.monotonic()  # recently probed: property must not probe

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
    client._session_checked_at = time.monotonic()
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


# --- read-side session recovery (no network: stubbed site + probe) ---
#
# mwclient asserts the user only on writes, so a session that expired
# server-side reads as anonymous: restricted namespaces (DM:) answer
# `accessdenied` while public pages keep working. These tests cover the
# read-side recovery that mirrors _write_with_relogin.


class _FakePage:
    name = "DM:Home"
    exists = True
    touched = None
    revision = 42

    def __init__(self, failures=1):
        self._failures = failures
        self.text_calls = 0

    def text(self):
        self.text_calls += 1
        if self.text_calls <= self._failures:
            raise mwclient.errors.APIError(
                "accessdenied", "You are not allowed to view DM:Home.", {}
            )
        return "# DM"

    def categories(self):
        return []


class _FakeSite:
    """Minimal stand-in: pages lookup + a userinfo probe answering `user_id`."""

    def __init__(self, page, user_id=0):
        self.pages = {page.name: page}
        self._user_id = user_id

    def api(self, action, http_method="POST", **kwargs):
        assert action == "query" and kwargs.get("meta") == "userinfo"
        return {"query": {"userinfo": {"id": self._user_id}}}


def make_read_client(page, user_id=0):
    client = make_client(bot_username="bot@example")
    client._site = _FakeSite(page, user_id=user_id)
    client._session_checked_at = time.monotonic()  # session was fresh at init
    return client


def test_read_retries_once_after_session_goes_stale(monkeypatch):
    """accessdenied from a degraded session triggers a re-login + one retry."""
    client = make_read_client(_FakePage(failures=1), user_id=0)

    relogins = []
    monkeypatch.setattr(client, "_login", lambda site: relogins.append(site))

    result = client.get_page("DM:Home")
    assert result["text"] == "# DM"
    assert result["exists"] is True
    assert result["last_revision_id"] == 42
    assert client._site.pages["DM:Home"].text_calls == 2  # failed once, retried once
    assert len(relogins) == 1  # re-authenticated exactly once


def test_read_propagates_real_permission_denial(monkeypatch):
    """A page the authenticated bot may not read surfaces unchanged."""
    client = make_read_client(_FakePage(failures=5), user_id=2)  # probe: still logged in

    monkeypatch.setattr(
        client, "_login", lambda site: pytest.fail("must not re-login when still authenticated")
    )

    with pytest.raises(mwclient.errors.APIError, match="accessdenied"):
        client.get_page("DM:Home")
    assert client._site.pages["DM:Home"].text_calls == 1  # no retry
    # and it does not loop on a retry that keeps failing
    client2 = make_read_client(_FakePage(failures=5), user_id=0)
    relogins = []
    monkeypatch.setattr(client2, "_login", lambda site: relogins.append(site))
    with pytest.raises(mwclient.errors.APIError, match="accessdenied"):
        client2.get_page("DM:Home")
    assert client2._site.pages["DM:Home"].text_calls == 2  # one retry only
    assert len(relogins) == 1


def test_read_never_recovers_without_credentials(monkeypatch):
    """With no bot credentials there is nothing to recover with."""
    client = make_client(bot_username="")
    client._site = _FakeSite(_FakePage(failures=1))
    client._session_checked_at = time.monotonic()

    monkeypatch.setattr(
        client, "_login", lambda site: pytest.fail("must not re-login without credentials")
    )

    with pytest.raises(mwclient.errors.APIError, match="accessdenied"):
        client.get_page("DM:Home")


def test_site_property_relogins_after_recheck_interval(monkeypatch):
    """Accessing .site past the recheck interval heals a degraded session."""
    client = make_client(bot_username="bot@example")
    client._site = _FakeSite(_FakePage(), user_id=0)
    client._session_checked_at = 0.0  # long ago

    relogins = []
    monkeypatch.setattr(client, "_login", lambda site: relogins.append(site))

    assert client.site is client._site
    assert len(relogins) == 1
    assert client._session_checked_at > 0.0
    client.site  # within the new interval: no further probe or re-login
    assert len(relogins) == 1


def test_site_property_skips_probe_within_interval():
    """Within the recheck interval, .site does not pay the probe round-trip."""
    client = make_client(bot_username="bot@example")
    client._site = _FakeSite(_FakePage())
    client._session_checked_at = time.monotonic()

    assert client.site is client._site  # no api() call — _FakeSite.api asserts on misuse

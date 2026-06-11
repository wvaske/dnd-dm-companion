"""High-level MediaWiki client for campaign-lore operations.

Wraps mwclient with the conventions this project relies on:
- every write carries an edit summary (audit trail in page history)
- writes are tagged as bot edits
- a read-only mode that hard-blocks all writes
- plain-dict return values so callers (MCP tools, scripts) can serialize freely
"""

from __future__ import annotations

import re
import time
from itertools import islice
from typing import Any
from urllib.parse import urlparse

import mwclient

from dm_companion.config import Settings, load_settings

_TAG_RE = re.compile(r"<[^>]+>")

WRITE_MODES = ("replace", "append", "prepend", "create")


class WikiError(RuntimeError):
    """Raised for wiki operations that fail in an expected, reportable way."""


def _strip_html(text: str) -> str:
    return _TAG_RE.sub("", text or "")


def _fmt_time(value: Any) -> str | None:
    """Normalize mwclient timestamps (struct_time or ISO string) to ISO 8601."""
    if value is None:
        return None
    if isinstance(value, time.struct_time):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", value)
    return str(value)


class WikiClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()
        self._site: mwclient.Site | None = None

    @property
    def site(self) -> mwclient.Site:
        if self._site is None:
            parsed = urlparse(self.settings.wiki_url)
            path = parsed.path or "/"
            if not path.endswith("/"):
                path += "/"
            site = mwclient.Site(parsed.netloc, scheme=parsed.scheme or "https", path=path)
            if self.settings.bot_username:
                site.login(self.settings.bot_username, self.settings.bot_password)
            self._site = site
        return self._site

    # ------------------------------------------------------------------ reads

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Full-text search (CirrusSearch syntax supported, e.g. incategory:NPCs)."""
        results = []
        for hit in islice(self.site.search(query), limit):
            results.append(
                {
                    "title": hit.get("title"),
                    "snippet": _strip_html(hit.get("snippet", "")),
                    "wordcount": hit.get("wordcount"),
                    "timestamp": hit.get("timestamp"),
                }
            )
        return results

    def get_page(self, title: str) -> dict:
        page = self.site.pages[title]
        if not page.exists:
            return {"title": title, "exists": False, "text": None, "categories": []}
        return {
            "title": page.name,
            "exists": True,
            "text": page.text(),
            "categories": [c.name for c in page.categories()],
            "last_modified": _fmt_time(page.touched),
            "last_revision_id": page.revision,
        }

    def list_category(self, category: str, limit: int = 100) -> list[str]:
        name = category.removeprefix("Category:")
        return [p.name for p in islice(self.site.categories[name], limit)]

    def list_pages(self, prefix: str = "", limit: int = 100) -> list[str]:
        pages = self.site.allpages(prefix=prefix) if prefix else self.site.allpages()
        return [p.name for p in islice(pages, limit)]

    def recent_changes(self, limit: int = 25) -> list[dict]:
        changes = []
        for rc in islice(self.site.recentchanges(), limit):
            changes.append(
                {
                    "type": rc.get("type"),
                    "title": rc.get("title"),
                    "user": rc.get("user"),
                    "comment": rc.get("comment"),
                    "timestamp": _fmt_time(rc.get("timestamp")),
                }
            )
        return changes

    def page_history(self, title: str, limit: int = 10) -> list[dict]:
        page = self.site.pages[title]
        if not page.exists:
            raise WikiError(f"Page does not exist: {title}")
        revisions = []
        for rev in islice(page.revisions(prop="ids|timestamp|user|comment"), limit):
            revisions.append(
                {
                    "revid": rev.get("revid"),
                    "user": rev.get("user"),
                    "comment": rev.get("comment"),
                    "timestamp": _fmt_time(rev.get("timestamp")),
                }
            )
        return revisions

    # ----------------------------------------------------------------- writes

    def save_page(
        self,
        title: str,
        text: str,
        summary: str,
        mode: str = "replace",
        minor: bool = False,
    ) -> dict:
        """Write a page. `mode` is one of replace/append/prepend/create.

        - replace: overwrite the full page (creates it if missing)
        - append/prepend: add to existing content (creates it if missing)
        - create: fail if the page already exists (safe for new entities)
        """
        if self.settings.read_only:
            raise WikiError("Wiki client is in read-only mode (DMC_READ_ONLY is set).")
        if not summary.strip():
            raise WikiError("An edit summary is required for every write.")
        if mode not in WRITE_MODES:
            raise WikiError(f"Unknown write mode {mode!r}; expected one of {WRITE_MODES}.")

        page = self.site.pages[title]
        existed = page.exists

        if mode == "create" and existed:
            raise WikiError(
                f"Page already exists: {title}. Read it and use append/replace instead."
            )
        if mode == "append" and existed:
            text = page.text().rstrip("\n") + "\n\n" + text
        elif mode == "prepend" and existed:
            text = text.rstrip("\n") + "\n\n" + page.text()

        result = page.save(text, summary=summary, minor=minor, bot=True)
        return {
            "title": page.name,
            "created": not existed,
            "revision_id": result.get("newrevid"),
            "summary": summary,
        }

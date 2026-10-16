"""Access-control verification for the gated DM namespaces.

The wiki hides DM material behind namespace gating (MediaWiki Lockdown):
`DM:` (3000) and `DM talk:` (3001) are readable only by the dm group. Skills
that write DM material rely on that gating, so `dmc check` verifies it the
same way an attacker would: fetch a gated page anonymously and require the
read to be denied. A page that comes back with content anonymously is a leak,
not a warning.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

# Gated namespaces this deployment relies on.
GATED_NAMESPACES: dict[str, int] = {"DM": 3000, "DM talk": 3001}

# Pages to probe anonymously. DM:Home is the Codex (must exist); the DM talk
# probe page was created for access-control verification and left in place.
PROBE_PAGES: tuple[str, ...] = ("DM:Home", "DM talk:Test Access Controls")

_USER_AGENT = "dmc-check/1.0 (wiki access-control verification)"


def _anonymous_get(url: str, timeout: float = 10.0) -> dict:
    """GET a URL with no credentials, returning the JSON body.

    MediaWiki reports permission errors in the response body (often alongside
    a non-200 status), so an HTTPError's body is the data we need, not a
    failure.
    """
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return json.loads(body)


def check_namespace_gating(wiki_url: str, fetch=_anonymous_get) -> list[str]:
    """Verify the gated DM namespaces exist and deny anonymous reads.

    Returns a list of problem strings; an empty list means the namespaces
    exist, hide their pages from anonymous readers, and are safe to write
    DM material to.
    """
    problems: list[str] = []
    base = wiki_url.rstrip("/")

    # 1. The namespaces exist at all.
    try:
        siteinfo = fetch(
            f"{base}/api.php?action=query&meta=siteinfo"
            "&siprop=namespaces&format=json"
        )
        namespaces = siteinfo.get("query", {}).get("namespaces", {})
    except Exception as exc:
        return [f"cannot read namespace list ({exc}) — is the wiki reachable?"]
    for name, ns_id in GATED_NAMESPACES.items():
        if str(ns_id) not in namespaces:
            problems.append(
                f"namespace {name} ({ns_id}) does not exist on this wiki"
            )

    # 2. Anonymous reads of gated pages are denied — the actual gate.
    for title in PROBE_PAGES:
        url = (
            f"{base}/api.php?action=query&titles={urllib.parse.quote(title)}"
            "&prop=revisions&rvprop=content&format=json"
        )
        try:
            payload = fetch(url)
        except Exception as exc:
            problems.append(
                f"anonymous probe of {title} failed with a network error ({exc})"
            )
            continue
        pages = payload.get("query", {}).get("pages", {})
        page = next(iter(pages.values()), {}) if pages else {}
        if "revisions" in page:
            problems.append(
                f"LEAK: {title} is readable WITHOUT credentials — the namespace "
                "is not gated; do not write DM material until this is fixed"
            )
        elif payload.get("error", {}).get("code") == "accessdenied":
            pass  # the gate works
        elif page.get("missing") is not None:
            problems.append(
                f"probe page {title} does not exist — gating cannot be verified "
                "for it (create it or adjust PROBE_PAGES)"
            )
        else:
            problems.append(
                f"anonymous probe of {title} returned an unexpected response"
            )
    return problems

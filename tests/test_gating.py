import pytest

from dm_companion.wiki.gating import check_namespace_gating

NAMESPACES_OK = {
    "query": {
        "namespaces": {
            "0": {"*": ""},
            "3000": {"*": "DM"},
            "3001": {"*": "DM talk"},
        }
    }
}

DENIED = {"error": {"code": "accessdenied", "info": "You are not allowed to view DM:Home."}}

LEAK = {
    "query": {
        "pages": {"1": {"title": "DM:Home", "revisions": [{"content": "secret plot"}]}}
    }
}

MISSING = {"query": {"pages": {"-1": {"title": "DM:Home", "missing": ""}}}}


def _fetcher(responses: dict[str, dict]):
    """Fake fetch keyed on URL substrings."""

    def fetch(url: str) -> dict:
        for needle, payload in responses.items():
            if needle in url:
                return payload
        raise AssertionError(f"unexpected url in fake fetch: {url}")

    return fetch


def _all_denied():
    return _fetcher(
        {
            "siteinfo": NAMESPACES_OK,
            "titles=DM%3AHome": DENIED,
            "Test%20Access": DENIED,
        }
    )


def test_gating_passes_when_reads_denied():
    assert check_namespace_gating("https://wiki.example", fetch=_all_denied()) == []


def test_gating_flags_leaked_page():
    fetch = _fetcher(
        {
            "siteinfo": NAMESPACES_OK,
            "titles=DM%3AHome": LEAK,
            "Test%20Access": DENIED,
        }
    )
    problems = check_namespace_gating("https://wiki.example", fetch=fetch)
    assert len(problems) == 1
    assert "LEAK" in problems[0]
    assert "DM:Home" in problems[0]
    assert "do not write DM material" in problems[0]


def test_gating_flags_missing_probe_page():
    fetch = _fetcher(
        {
            "siteinfo": NAMESPACES_OK,
            "titles=DM%3AHome": DENIED,
            "Test%20Access": MISSING,
        }
    )
    problems = check_namespace_gating("https://wiki.example", fetch=fetch)
    assert len(problems) == 1
    assert "does not exist" in problems[0]


def test_gating_flags_absent_namespace():
    siteinfo = {"query": {"namespaces": {"0": {"*": ""}, "3000": {"*": "DM"}}}}
    fetch = _fetcher(
        {
            "siteinfo": siteinfo,
            "titles=DM%3AHome": DENIED,
            "Test%20Access": DENIED,
        }
    )
    problems = check_namespace_gating("https://wiki.example", fetch=fetch)
    assert len(problems) == 1
    assert "DM talk" in problems[0]
    assert "3001" in problems[0]


def test_gating_reports_unreachable_wiki():
    def fetch(url: str) -> dict:
        raise ConnectionError("refused")

    problems = check_namespace_gating("https://wiki.example", fetch=fetch)
    assert len(problems) == 1
    assert "cannot read namespace list" in problems[0]


def test_gating_reports_probe_network_error():
    def fetch(url: str) -> dict:
        if "siteinfo" in url:
            return NAMESPACES_OK
        raise ConnectionError("refused")

    problems = check_namespace_gating("https://wiki.example", fetch=fetch)
    assert len(problems) == 2  # both probes failed
    assert all("network error" in problem for problem in problems)


def test_gating_flags_unexpected_response():
    fetch = _fetcher(
        {
            "siteinfo": NAMESPACES_OK,
            "titles=DM%3AHome": {"batchcomplete": ""},
            "Test%20Access": DENIED,
        }
    )
    problems = check_namespace_gating("https://wiki.example", fetch=fetch)
    assert len(problems) == 1
    assert "unexpected response" in problems[0]


def test_probe_urls_are_valid():
    # Guard the URL construction directly: every probe page must be quoted
    # into a well-formed api.php URL.
    import urllib.parse

    for title in ("DM:Home", "DM talk:Test Access Controls"):
        url = "https://wiki.example/api.php?action=query&titles=" + urllib.parse.quote(title)
        parsed = urllib.parse.urlparse(url)
        assert parsed.path == "/api.php"
        assert "titles=" in urllib.parse.unquote(parsed.query)

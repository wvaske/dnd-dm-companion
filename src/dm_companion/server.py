"""MCP server exposing the campaign wiki to any MCP host.

Works with opencode, Claude Code, Claude Desktop, or anything else that
speaks the Model Context Protocol over stdio. All wiki access goes through
dm_companion.wiki.WikiClient, so the same behavior (edit summaries, bot
flags, read-only enforcement) applies regardless of which host calls in.

Run with: dm-companion-mcp  (after `uv sync` / `pip install -e .`)
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from dm_companion.wiki import WikiClient

mcp = FastMCP("dnd-campaign-wiki")

_client: WikiClient | None = None


def _wiki() -> WikiClient:
    global _client
    if _client is None:
        _client = WikiClient()
    return _client


@mcp.tool()
def search_wiki(query: str, limit: int = 10) -> list[dict]:
    """Full-text search of the campaign wiki (CirrusSearch).

    Supports advanced syntax: `incategory:NPCs dragon`, `intitle:Waterdeep`,
    `prefix:Session`. Returns titles with content snippets. Always search
    before creating a page — the entity may already exist under another name.
    """
    return _wiki().search(query, limit=limit)


@mcp.tool()
def read_page(title: str) -> dict:
    """Read a wiki page's full wikitext, categories, and last-modified info.

    Returns exists=False (rather than an error) if the page is missing.
    """
    return _wiki().get_page(title)


@mcp.tool()
def write_page(
    title: str,
    content: str,
    summary: str,
    mode: str = "replace",
    minor: bool = False,
) -> dict:
    """Create or edit a wiki page. An edit summary is mandatory.

    Modes:
      - "create": new pages only; fails if the title exists (safest default
        for new entities — prevents accidental overwrites)
      - "replace": overwrite the entire page (read it first!)
      - "append" / "prepend": add a section without touching existing content

    Content is MediaWiki wikitext. Follow the wiki's existing templates and
    category conventions; check a similar page first if unsure.
    """
    return _wiki().save_page(title, content, summary=summary, mode=mode, minor=minor)


@mcp.tool()
def find_related_lore(query: str, limit: int = 8) -> dict:
    """Semantic search over campaign lore — finds pages related in *meaning*.

    Complements search_wiki (keyword/CirrusSearch): use this for conceptual
    questions like "what do we know that connects to the Cult of the Dragon?"
    where the relevant pages may not contain the query's words. Results come
    from a local embeddings index built with `dmc index`; if results seem
    stale or empty, ask the DM to re-run it.
    """
    from dm_companion.embeddings import EmbeddingsClient
    from dm_companion.lore_index import LoreIndex

    settings = _wiki().settings
    index = LoreIndex(settings.index_path)
    try:
        stats = index.stats()
        if stats["pages"] == 0:
            return {
                "matches": [],
                "error": "The lore index is empty. Build it with: dmc index",
            }
        embedder = EmbeddingsClient.from_settings(settings)
        query_vector = embedder.embed([query])[0]
        return {"matches": index.search(query_vector, limit=limit), "index": stats}
    finally:
        index.close()


@mcp.tool()
def upload_image(
    path: str,
    summary: str,
    filename: str = "",
    description: str = "",
    ignore_warnings: bool = False,
) -> dict:
    """Upload a local image (token art, map, handout) to the wiki.

    `summary` is the upload log comment (mandatory). `description` becomes the
    File: page wikitext — include a caption and a category, e.g.
    "Map of Parnast [[Category:Maps]]". Reference the result in pages with
    [[File:<filename>|thumb|<caption>]].

    A "Warning" result means MediaWiki held the upload back (usually a
    duplicate); report the warning to the DM rather than retrying with
    ignore_warnings=True on your own.
    """
    return _wiki().upload_image(
        path,
        summary=summary,
        filename=filename or None,
        description=description,
        ignore_warnings=ignore_warnings,
    )


@mcp.tool()
def list_category(category: str, limit: int = 100) -> list[str]:
    """List page titles in a category (e.g. "NPCs", "Locations", "Sessions")."""
    return _wiki().list_category(category, limit=limit)


@mcp.tool()
def list_pages(prefix: str = "", limit: int = 100) -> list[str]:
    """List page titles, optionally filtered by title prefix (e.g. "Session")."""
    return _wiki().list_pages(prefix=prefix, limit=limit)


@mcp.tool()
def recent_changes(limit: int = 25) -> list[dict]:
    """Recent edits across the wiki: who changed what, when, and why."""
    return _wiki().recent_changes(limit=limit)


@mcp.tool()
def page_history(title: str, limit: int = 10) -> list[dict]:
    """Revision history for one page (revision ids, users, edit summaries)."""
    return _wiki().page_history(title, limit=limit)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

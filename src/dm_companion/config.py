"""Configuration for the DM companion.

All settings come from environment variables (optionally loaded from a .env
file in the working directory). This keeps the companion usable from any MCP
host or shell without a config-file format to maintain.

Variables:
    MEDIAWIKI_URL   Full URL of the wiki, e.g. https://wiki.deeznuts.wiki
                    (api.php must live at <url>/api.php)
    BOT_USERNAME    MediaWiki bot username, e.g. User@botname
    BOT_PASSWORD    MediaWiki bot password
    DMC_READ_ONLY   Set to "1"/"true" to refuse all wiki writes
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    wiki_url: str
    bot_username: str
    bot_password: str
    read_only: bool
    # Semantic search (optional). Any OpenAI-compatible embeddings endpoint:
    # Ollama, LiteLLM, OpenRouter, OpenAI, ... NOT an LLM SDK — plain HTTP.
    embeddings_url: str = ""
    embeddings_model: str = ""
    embeddings_api_key: str = ""
    index_path: str = "lore_index.db"


def load_settings() -> Settings:
    load_dotenv()
    url = os.environ.get("MEDIAWIKI_URL", "").strip().rstrip("/")
    username = os.environ.get("BOT_USERNAME", "").strip()
    password = os.environ.get("BOT_PASSWORD", "").strip()
    read_only = os.environ.get("DMC_READ_ONLY", "").lower() in ("1", "true", "yes")

    if not url:
        raise RuntimeError(
            "MEDIAWIKI_URL is not set. Copy .env.example to .env and fill it in."
        )
    return Settings(
        wiki_url=url,
        bot_username=username,
        bot_password=password,
        read_only=read_only,
        embeddings_url=os.environ.get("EMBEDDINGS_URL", "").strip().rstrip("/"),
        embeddings_model=os.environ.get("EMBEDDINGS_MODEL", "").strip(),
        embeddings_api_key=os.environ.get("EMBEDDINGS_API_KEY", "").strip(),
        index_path=os.environ.get("DMC_INDEX_PATH", "lore_index.db").strip(),
    )

import pytest

from dm_companion.indexing import (
    IndexingError,
    chunk_markdown,
    ingest_book,
    slugify,
    sync_wiki,
)
from dm_companion.vector_store import SqliteVectorStore


@pytest.fixture
def store(tmp_path):
    s = SqliteVectorStore(tmp_path / "test_index.db")
    yield s
    s.close()


class _FakeWiki:
    def __init__(self, pages_by_ns):
        self.pages_by_ns = pages_by_ns  # ns -> {title: text}

    def list_pages(self, limit=None, namespace=0, prefix=""):
        return list(self.pages_by_ns.get(namespace, {}))

    def get_page(self, title):
        for pages in self.pages_by_ns.values():
            if title in pages:
                return {"title": title, "exists": True, "text": pages[title]}
        return {"title": title, "exists": False, "text": None}


class _FakeEmbedder:
    model = "fake-model"

    def __init__(self):
        self.embedded = []

    def embed(self, texts, batch_size=16):
        self.embedded.extend(texts)
        return [[float(len(t)), 1.0] for t in texts]


# ----------------------------------------------------------------- wiki sync


def test_sync_wiki_incremental(store):
    wiki = _FakeWiki({0: {"Tiamat": "dragon goddess", "Waterdeep": "city"}})
    embedder = _FakeEmbedder()

    summary = sync_wiki(wiki, embedder, store)
    assert summary["embedded"] == 2 and summary["unchanged"] == 0
    assert store.stats()["sources"] == {"wiki": 2}

    # Second run: nothing changed, nothing re-embedded.
    embedder.embedded.clear()
    summary = sync_wiki(wiki, embedder, store)
    assert summary["embedded"] == 0 and summary["unchanged"] == 2
    assert embedder.embedded == []

    # Change one page, delete another: one re-embed, one removal.
    wiki.pages_by_ns[0]["Tiamat"] = "dragon goddess, slain in Session 30"
    del wiki.pages_by_ns[0]["Waterdeep"]
    summary = sync_wiki(wiki, embedder, store)
    assert summary["embedded"] == 1
    assert summary["removed"] == ["wiki::Waterdeep"]

    # --full re-embeds even unchanged pages.
    summary = sync_wiki(wiki, embedder, store, full=True)
    assert summary["embedded"] == 1 and summary["unchanged"] == 0


def test_sync_wiki_extra_namespace_tagged_as_reference(store):
    wiki = _FakeWiki(
        {
            0: {"Tiamat": "campaign take on Tiamat"},
            3000: {"Sourcebook:Rise of Tiamat": "official adventure text"},
        }
    )
    sync_wiki(wiki, _FakeEmbedder(), store, namespaces=(0, 3000))

    assert store.stats()["sources"] == {"wiki": 1, "wiki:Sourcebook": 1}
    official = store.search([1.0, 1.0], scope="official")
    assert [r["title"] for r in official] == ["Sourcebook:Rise of Tiamat"]


def test_sync_wiki_does_not_touch_books(store):
    store.upsert("book::phb::00000", "book:phb", "PHB", "h", "s", [1.0, 1.0])
    wiki = _FakeWiki({0: {"Tiamat": "dragon goddess"}})
    summary = sync_wiki(wiki, _FakeEmbedder(), store)
    assert summary["removed"] == []
    assert store.get_hash("book::phb::00000") is not None


# --------------------------------------------------------------------- books


def test_slugify():
    assert slugify("Player's Handbook") == "player-s-handbook"
    with pytest.raises(IndexingError):
        slugify("***")


def test_chunk_markdown_heading_breadcrumbs():
    text = (
        "intro before any heading\n"
        "# Chapter 1\n"
        "races overview\n"
        "## Elves\n"
        "elf lore\n"
        "## Dwarves\n"
        "dwarf lore\n"
        "# Chapter 2\n"
        "classes\n"
    )
    chunks = chunk_markdown(text)
    headings = [c.heading for c in chunks]
    assert headings == [
        "(beginning)",
        "Chapter 1",
        "Chapter 1 > Elves",
        "Chapter 1 > Dwarves",
        "Chapter 2",
    ]
    assert chunks[2].text == "elf lore"


def test_chunk_markdown_splits_oversized_sections():
    text = "# Big\n" + "x" * 9000
    chunks = chunk_markdown(text, max_chars=4000)
    assert len(chunks) == 3
    assert all(c.heading == "Big" for c in chunks)
    assert sum(len(c.text) for c in chunks) == 9000


def test_chunk_markdown_plain_text():
    chunks = chunk_markdown("just plain text, no headings")
    assert len(chunks) == 1
    assert chunks[0].heading == "(beginning)"


def test_ingest_book_roundtrip(tmp_path, store):
    book = tmp_path / "phb.md"
    book.write_text("# Chapter 1\nraces\n## Elves\nelf lore\n")
    embedder = _FakeEmbedder()

    summary = ingest_book(book, title="Player's Handbook", embedder=embedder, store=store)
    assert summary["source"] == "book:player-s-handbook"
    assert summary["chunks"] == 2 and summary["embedded"] == 2
    # Book title + breadcrumb are embedded with the chunk text.
    assert embedder.embedded[0].startswith("Player's Handbook — Chapter 1")

    # Re-ingest unchanged: all skipped by hash.
    summary = ingest_book(book, title="Player's Handbook", embedder=embedder, store=store)
    assert summary["embedded"] == 0 and summary["unchanged"] == 2

    # Shrink the book: stale trailing chunks are pruned.
    book.write_text("# Chapter 1\nraces only now\n")
    summary = ingest_book(book, title="Player's Handbook", embedder=embedder, store=store)
    assert summary["chunks"] == 1
    assert summary["removed"] == ["book::player-s-handbook::00001"]

    results = store.search([1.0, 1.0], scope="official")
    assert results[0]["source"] == "book:player-s-handbook"


def test_ingest_book_rejects_pdf(tmp_path, store):
    pdf = tmp_path / "phb.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    with pytest.raises(IndexingError, match="pdftotext"):
        ingest_book(pdf, title="PHB", embedder=_FakeEmbedder(), store=store)


def test_ingest_book_rejects_missing_file(store):
    with pytest.raises(IndexingError, match="not found"):
        ingest_book("/nope.md", title="PHB", embedder=_FakeEmbedder(), store=store)

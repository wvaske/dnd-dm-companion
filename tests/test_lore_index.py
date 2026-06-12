import pytest

from dm_companion import embeddings as emb_mod
from dm_companion.embeddings import EmbeddingsClient, EmbeddingsError, cosine_similarity
from dm_companion.lore_index import LoreIndex, _content_hash, _snippet


@pytest.fixture
def index(tmp_path):
    idx = LoreIndex(tmp_path / "test_index.db")
    yield idx
    idx.close()


def test_cosine_similarity():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert cosine_similarity([1.0, 1.0], [-1.0, -1.0]) == pytest.approx(-1.0)


def test_cosine_dimension_mismatch_explains_rebuild():
    with pytest.raises(EmbeddingsError, match="dmc index --full"):
        cosine_similarity([1.0, 0.0], [1.0, 0.0, 0.0])


def test_upsert_and_search_orders_by_similarity(index):
    index.upsert("Tiamat", "h1", "dragon goddess", [1.0, 0.0])
    index.upsert("Waterdeep", "h2", "city of splendors", [0.0, 1.0])
    index.upsert("Cult of the Dragon", "h3", "dragon cult", [0.9, 0.1])

    results = index.search([1.0, 0.0], limit=2)
    assert [r["title"] for r in results] == ["Tiamat", "Cult of the Dragon"]
    assert results[0]["score"] > results[1]["score"]
    assert results[0]["snippet"] == "dragon goddess"


def test_upsert_replaces_existing(index):
    index.upsert("Tiamat", "h1", "old", [1.0, 0.0])
    index.upsert("Tiamat", "h2", "new", [0.0, 1.0])
    assert index.stats()["pages"] == 1
    assert index.get_hash("Tiamat") == "h2"


def test_remove_absent(index):
    index.upsert("Keep", "h1", "s", [1.0])
    index.upsert("Deleted Page", "h2", "s", [1.0])
    removed = index.remove_absent({"Keep", "Other"})
    assert removed == ["Deleted Page"]
    assert index.get_hash("Deleted Page") is None
    assert index.get_hash("Keep") == "h1"


def test_stats_meta(index):
    assert index.stats() == {"pages": 0, "indexed_at": None, "embeddings_model": None}
    index.set_meta("indexed_at", "2026-06-12T00:00:00Z")
    index.set_meta("embeddings_model", "test-model")
    stats = index.stats()
    assert stats["indexed_at"] == "2026-06-12T00:00:00Z"
    assert stats["embeddings_model"] == "test-model"


def test_content_hash_changes_with_content():
    assert _content_hash("a") != _content_hash("b")
    assert _content_hash("a") == _content_hash("a")


def test_snippet_strips_wikitext_noise():
    text = "{{NPC|status=Active}}\nA five-headed dragon goddess.\n[[Category:NPCs]]"
    assert _snippet(text) == "A five-headed dragon goddess."


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self):
        return self._payload


def test_embeddings_client_batches_and_preserves_order(monkeypatch):
    calls = []

    def fake_post(url, json=None, headers=None, timeout=None):
        calls.append((url, json, headers))
        # Return vectors out of order to prove sorting by index works.
        data = [
            {"index": i, "embedding": [float(hash(text) % 100)]}
            for i, text in enumerate(json["input"])
        ]
        return _FakeResponse({"data": list(reversed(data))})

    monkeypatch.setattr(emb_mod.requests, "post", fake_post)

    client = EmbeddingsClient("http://localhost:11434/v1", "test-model", api_key="sk-x")
    texts = [f"page {i}" for i in range(20)]
    vectors = client.embed(texts, batch_size=16)

    assert len(vectors) == 20
    assert len(calls) == 2  # 16 + 4
    assert calls[0][0] == "http://localhost:11434/v1/embeddings"
    assert calls[0][1]["model"] == "test-model"
    assert calls[0][2]["Authorization"] == "Bearer sk-x"
    assert vectors[3] == [float(hash("page 3") % 100)]


def test_embeddings_client_requires_config():
    with pytest.raises(EmbeddingsError, match="EMBEDDINGS_URL"):
        EmbeddingsClient("", "")


def test_embeddings_client_http_error(monkeypatch):
    monkeypatch.setattr(
        emb_mod.requests, "post", lambda *a, **k: _FakeResponse({"error": "nope"}, 500)
    )
    client = EmbeddingsClient("http://x/v1", "m")
    with pytest.raises(EmbeddingsError, match="500"):
        client.embed(["text"])


class _FakeWiki:
    def __init__(self, pages):
        self.pages = pages  # title -> text

    def list_pages(self, limit=None):
        return list(self.pages)

    def get_page(self, title):
        return {"title": title, "exists": True, "text": self.pages[title]}


class _FakeEmbedder:
    model = "fake-model"

    def __init__(self):
        self.embedded = []

    def embed(self, texts, batch_size=16):
        self.embedded.extend(texts)
        return [[float(len(t)), 1.0] for t in texts]


def test_build_index_incremental(index):
    from dm_companion.lore_index import build_index

    wiki = _FakeWiki({"Tiamat": "dragon goddess", "Waterdeep": "city"})
    embedder = _FakeEmbedder()

    summary = build_index(wiki, embedder, index)
    assert summary["embedded"] == 2 and summary["unchanged"] == 0
    assert index.stats()["pages"] == 2
    assert index.stats()["embeddings_model"] == "fake-model"

    # Second run: nothing changed, nothing re-embedded.
    embedder.embedded.clear()
    summary = build_index(wiki, embedder, index)
    assert summary["embedded"] == 0 and summary["unchanged"] == 2
    assert embedder.embedded == []

    # Change one page, delete another: one re-embed, one removal.
    wiki.pages["Tiamat"] = "dragon goddess, slain in Session 30"
    del wiki.pages["Waterdeep"]
    summary = build_index(wiki, embedder, index)
    assert summary["embedded"] == 1
    assert summary["removed"] == ["Waterdeep"]
    assert index.stats()["pages"] == 1

    # --full re-embeds even unchanged pages.
    summary = build_index(wiki, embedder, index, full=True)
    assert summary["embedded"] == 1 and summary["unchanged"] == 0

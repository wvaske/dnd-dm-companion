import pytest

from dm_companion.config import Settings
from dm_companion.vector_store import (
    OpenSearchVectorStore,
    SqliteVectorStore,
    VectorStoreError,
    open_vector_store,
)


@pytest.fixture
def store(tmp_path):
    s = SqliteVectorStore(tmp_path / "test_index.db")
    yield s
    s.close()


def _doc(store, doc_id, source, vec, title=None):
    store.upsert(doc_id, source, title or doc_id, f"hash-{doc_id}", f"snippet {doc_id}", vec)


def test_upsert_and_search_orders_by_similarity(store):
    _doc(store, "wiki::Tiamat", "wiki", [1.0, 0.0], title="Tiamat")
    _doc(store, "wiki::Waterdeep", "wiki", [0.0, 1.0], title="Waterdeep")
    _doc(store, "wiki::Cult", "wiki", [0.9, 0.1], title="Cult of the Dragon")

    results = store.search([1.0, 0.0], limit=2)
    assert [r["title"] for r in results] == ["Tiamat", "Cult of the Dragon"]
    assert results[0]["score"] > results[1]["score"]
    assert results[0]["source"] == "wiki"


def test_scope_filtering(store):
    _doc(store, "wiki::Tiamat", "wiki", [1.0, 0.0])
    _doc(store, "wiki::Sourcebook:Dragons", "wiki:Sourcebook", [1.0, 0.0])
    _doc(store, "book::phb::00001", "book:phb", [1.0, 0.0])

    assert {r["source"] for r in store.search([1.0, 0.0], scope="all")} == {
        "wiki",
        "wiki:Sourcebook",
        "book:phb",
    }
    assert {r["source"] for r in store.search([1.0, 0.0], scope="campaign")} == {"wiki"}
    # Official = books AND reference wiki namespaces.
    assert {r["source"] for r in store.search([1.0, 0.0], scope="official")} == {
        "wiki:Sourcebook",
        "book:phb",
    }


def test_search_rejects_unknown_scope(store):
    with pytest.raises(VectorStoreError, match="scope"):
        store.search([1.0], scope="everything")


def test_upsert_replaces_existing(store):
    _doc(store, "wiki::Tiamat", "wiki", [1.0, 0.0])
    store.upsert("wiki::Tiamat", "wiki", "Tiamat", "h2", "new snippet", [0.0, 1.0])
    assert store.stats()["documents"] == 1
    assert store.get_hash("wiki::Tiamat") == "h2"


def test_remove_absent_is_prefix_scoped(store):
    _doc(store, "wiki::Keep", "wiki", [1.0])
    _doc(store, "wiki::Gone", "wiki", [1.0])
    _doc(store, "book::phb::00000", "book:phb", [1.0])

    removed = store.remove_absent("wiki::", {"wiki::Keep"})
    assert removed == ["wiki::Gone"]
    # Sourcebook chunks survive a wiki sync.
    assert store.get_hash("book::phb::00000") is not None


def test_delete_by_prefix(store):
    _doc(store, "book::phb::00000", "book:phb", [1.0])
    _doc(store, "book::phb::00001", "book:phb", [1.0])
    _doc(store, "wiki::Tiamat", "wiki", [1.0])

    assert store.delete_by_prefix("book::phb::") == 2
    assert store.stats()["documents"] == 1


def test_stats_groups_by_source(store):
    _doc(store, "wiki::A", "wiki", [1.0])
    _doc(store, "book::phb::00000", "book:phb", [1.0])
    _doc(store, "book::phb::00001", "book:phb", [1.0])
    store.set_meta("embeddings_model", "test-model")

    stats = store.stats()
    assert stats["backend"] == "sqlite"
    assert stats["documents"] == 3
    assert stats["sources"] == {"wiki": 1, "book:phb": 2}
    assert stats["embeddings_model"] == "test-model"


def _settings(**overrides):
    base = dict(
        wiki_url="https://wiki.example.invalid",
        bot_username="",
        bot_password="",
        read_only=False,
    )
    base.update(overrides)
    return Settings(**base)


def test_factory_default_sqlite(tmp_path):
    store = open_vector_store(_settings(index_path=str(tmp_path / "x.db")))
    assert isinstance(store, SqliteVectorStore)
    store.close()


def test_factory_opensearch():
    store = open_vector_store(
        _settings(vector_backend="opensearch", opensearch_url="http://localhost:9200")
    )
    assert isinstance(store, OpenSearchVectorStore)


def test_factory_opensearch_requires_url():
    with pytest.raises(VectorStoreError, match="OPENSEARCH_URL"):
        open_vector_store(_settings(vector_backend="opensearch"))


def test_factory_rejects_unknown_backend():
    with pytest.raises(VectorStoreError, match="VECTOR_BACKEND"):
        open_vector_store(_settings(vector_backend="pinecone"))


class _FakeOpenSearch:
    """Request recorder with canned responses, attached as store._request."""

    def __init__(self, responses=None):
        self.calls = []
        self.responses = responses or {}

    def __call__(self, method, path, body=None, ok_404=False):
        self.calls.append((method, path, body))
        key = (method, path)
        if key in self.responses:
            return self.responses[key]
        if ok_404:
            return None
        return {}


def test_opensearch_creates_index_with_embedding_dimension():
    store = OpenSearchVectorStore("http://localhost:9200", index="test-lore")
    fake = _FakeOpenSearch()
    store._request = fake

    store.upsert("wiki::Tiamat", "wiki", "Tiamat", "h1", "snip", [0.1, 0.2, 0.3])

    create = next(c for c in fake.calls if c[0] == "PUT" and c[1] == "/test-lore")
    assert create[2]["mappings"]["properties"]["embedding"] == {
        "type": "knn_vector",
        "dimension": 3,
    }
    assert create[2]["settings"]["index"]["knn"] is True
    put_doc = next(c for c in fake.calls if c[1].startswith("/test-lore/_doc/"))
    assert put_doc[2]["doc_id"] == "wiki::Tiamat"
    assert put_doc[2]["source"] == "wiki"


def test_opensearch_scoped_search_overfetches_and_filters():
    store = OpenSearchVectorStore("http://localhost:9200", index="test-lore")
    hits = [
        {"_score": 0.9, "_source": {"source": "book:phb", "title": "PHB — Elves", "snippet": "s"}},
        {"_score": 0.8, "_source": {"source": "wiki", "title": "Thia", "snippet": "s"}},
        {"_score": 0.7, "_source": {"source": "book:phb", "title": "PHB — Combat", "snippet": "s"}},
    ]
    fake = _FakeOpenSearch(
        responses={("POST", "/test-lore/_search"): {"hits": {"hits": hits}}}
    )
    store._request = fake

    results = store.search([1.0, 0.0], limit=2, scope="official")
    assert [r["title"] for r in results] == ["PHB — Elves", "PHB — Combat"]

    search_body = next(c[2] for c in fake.calls if c[1] == "/test-lore/_search")
    assert search_body["query"]["knn"]["embedding"]["k"] == 8  # limit * 4 when scoped


def test_opensearch_search_handles_missing_index():
    store = OpenSearchVectorStore("http://localhost:9200", index="test-lore")
    store._request = _FakeOpenSearch(responses={("POST", "/test-lore/_search"): None})
    assert store.search([1.0], scope="all") == []

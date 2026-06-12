import pytest

from dm_companion import embeddings as emb_mod
from dm_companion.embeddings import EmbeddingsClient, EmbeddingsError, cosine_similarity


def test_cosine_similarity():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert cosine_similarity([1.0, 1.0], [-1.0, -1.0]) == pytest.approx(-1.0)


def test_cosine_dimension_mismatch_explains_rebuild():
    with pytest.raises(EmbeddingsError, match="dmc index --full"):
        cosine_similarity([1.0, 0.0], [1.0, 0.0, 0.0])


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

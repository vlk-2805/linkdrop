import pytest

import app as app_module


class FakePipeline:
    def __init__(self, cache):
        self.cache = cache
        self.key = None

    def incr(self, key):
        self.key = key
        return self

    def expire(self, key, seconds):
        return self

    def execute(self):
        self.cache.values[self.key] = int(self.cache.values.get(self.key, 0)) + 1


class FakeRedis:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def pipeline(self):
        return FakePipeline(self)

    def set(self, key, value):
        self.values[key] = value


class FakeCursor:
    def __init__(self, result):
        self.result = result
        self.query = None
        self.parameters = None

    def execute(self, query, parameters=None):
        self.query = query
        self.parameters = parameters

    def fetchone(self):
        return self.result

    def close(self):
        pass


class FakeConnection:
    def __init__(self, result):
        self.fake_cursor = FakeCursor(result)
        self.committed = False
        self.closed = False

    def cursor(self):
        return self.fake_cursor

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


@pytest.fixture
def client(monkeypatch):
    fake_cache = FakeRedis()
    monkeypatch.setattr(app_module, "cache", fake_cache)
    return app_module.app.test_client(), fake_cache


@pytest.mark.parametrize("number", [0, 1, 61, 62, 3_843, 123_456_789])
def test_base62_encoding_round_trips(number):
    encoded = app_module.base62_encode(number)

    assert app_module.base62_decode(encoded) == number


def test_health_endpoint(client):
    test_client, _ = client

    response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_shorten_requires_a_url(client):
    test_client, _ = client

    response = test_client.post("/shorten", json={})

    assert response.status_code == 400
    assert response.json == {"error": "Missing url field"}


def test_shorten_saves_url_and_returns_short_link(client, monkeypatch):
    test_client, fake_cache = client
    connection = FakeConnection((62,))
    monkeypatch.setattr(app_module, "get_db", lambda: connection)

    response = test_client.post(
        "/shorten", json={"url": "https://example.com/a/long/path"}
    )

    short_code = app_module.base62_encode(62)
    assert response.status_code == 201
    assert response.json == {
        "short_url": f"http://localhost:5000/{short_code}",
        "short_code": short_code,
    }
    assert fake_cache.values[short_code] == "https://example.com/a/long/path"
    assert connection.committed
    assert connection.closed


def test_redirect_uses_cached_url(client):
    test_client, fake_cache = client
    fake_cache.values["abc"] = "https://example.com/from-cache"

    response = test_client.get("/abc")

    assert response.status_code == 302
    assert response.location == "https://example.com/from-cache"


def test_redirect_loads_url_from_database_on_cache_miss(client, monkeypatch):
    test_client, fake_cache = client
    connection = FakeConnection(("https://example.com/from-database",))
    monkeypatch.setattr(app_module, "get_db", lambda: connection)

    response = test_client.get("/1")

    assert response.status_code == 302
    assert response.location == "https://example.com/from-database"
    assert connection.fake_cursor.parameters == (1,)
    assert fake_cache.values["1"] == "https://example.com/from-database"


def test_redirect_returns_404_for_unknown_code(client, monkeypatch):
    test_client, _ = client
    monkeypatch.setattr(app_module, "get_db", lambda: FakeConnection(None))

    response = test_client.get("/1")

    assert response.status_code == 404
    assert response.json == {"error": "Short URL not found"}


def test_shorten_is_rate_limited_after_ten_requests(client, monkeypatch):
    test_client, _ = client
    monkeypatch.setattr(app_module, "get_db", lambda: FakeConnection((1,)))

    responses = [
        test_client.post("/shorten", json={"url": "https://example.com"})
        for _ in range(11)
    ]

    assert all(response.status_code == 201 for response in responses[:10])
    assert responses[10].status_code == 429
    assert responses[10].json == {"error": "Rate limit exceeded. Try again later."}

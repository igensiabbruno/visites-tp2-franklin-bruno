from importlib.metadata import version


def test_root_increments(client):
    assert client.get("/").json() == {"visites": 1}
    assert client.get("/").json() == {"visites": 2}


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_redis_down(client, fake_server):
    fake_server.connected = False
    resp = client.get("/health")
    assert resp.status_code == 503
    assert resp.text == "redis down"


def test_metrics_counts_requests(client):
    client.get("/")
    body = client.get("/metrics").text
    assert 'http_requests_total{method="GET",path="/",status="200"}' in body
    assert "http_request_duration_seconds" in body


# --- TP01, membre A (feat/version-header) ---
def test_version_header(client):
    resp = client.get("/")
    # suit pyproject.toml, pas de valeur en dur
    assert resp.headers["X-Visites-Version"] == version("visites")


# --- TP01, membre B (feat/reset) ---
def test_reset(client):
    client.get("/")
    assert client.post("/reset").json() == {"visites": 0}
    assert client.get("/").json() == {"visites": 1}


def test_reset_redis_down(client, fake_server):
    """Ajouté après la demande de changement du relecteur (étape 4)."""
    fake_server.connected = False
    assert client.post("/reset").status_code == 503

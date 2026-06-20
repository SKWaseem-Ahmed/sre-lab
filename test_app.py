# Reason: even one test proves the CI "test" stage works and that the app imports cleanly.
from app import app

def test_healthz():
    client = app.test_client()
    r = client.get("/healthz")
    assert r.status_code == 200

def test_products():
    client = app.test_client()
    r = client.get("/api/products")
    assert r.status_code == 200
    assert len(r.get_json()) == 3
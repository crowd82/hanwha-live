import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_price_endpoint_returns_data():
    with patch("cache.get_cache") as mock_cache:
        mock_cache.return_value = {
            "price": 3480.0, "change": 80.0, "change_pct": 2.35,
            "volume": 1240500, "open": 3400.0,
            "high_52w": 4120.0, "low_52w": 2890.0, "market_cap_billion": 0,
        }
        resp = client.get("/api/price")
        assert resp.status_code == 200
        data = resp.json()
        assert data["price"] == 3480.0
        assert "change_pct" in data

def test_chart_endpoint_annual():
    with patch("cache.get_cache") as mock_cache:
        mock_cache.return_value = [{"time": "2025-01-01", "value": 2890.0, "volume": 100}]
        resp = client.get("/api/chart/annual")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

def test_chart_endpoint_invalid_period():
    resp = client.get("/api/chart/decade")
    assert resp.status_code == 400

def test_index_returns_html():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]

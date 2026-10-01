"""Tests for the API endpoints."""
import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, engine, Base

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_stats_endpoint():
    response = client.get("/api/stats/")
    assert response.status_code == 200
    data = response.json()
    assert "total_products_tracked" in data
    assert "total_competitors" in data


def test_discover_endpoint():
    response = client.get("/api/discover/?category=phones&max_products=3")
    assert response.status_code == 200
    data = response.json()
    assert "products_found" in data
    assert "urls" in data

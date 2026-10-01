"""Tests for discover endpoint."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_discover_phones_category():
    response = client.get("/api/discover/?category=phones&max_products=3")
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "phones"
    assert "products_found" in data
    assert "urls" in data


def test_discover_invalid_category():
    response = client.get("/api/discover/?category=invalid&max_products=3")
    assert response.status_code == 400
    assert "Unknown category" in response.json()["detail"]


def test_discover_computing_category():
    response = client.get("/api/discover/?category=computing&max_products=3")
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "computing"


def test_discover_appliances_category():
    response = client.get("/api/discover/?category=appliances&max_products=3")
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "appliances"

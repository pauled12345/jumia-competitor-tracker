"""Tests for Jumia URL validation."""
import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, engine, Base
from models import Competitor, Product

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    competitor = Competitor(name="Jumia", platform="jumia", url="https://www.jumia.co.ke")
    product = Product(user_id=1, name="Test", category="phones")
    db.add_all([competitor, product])
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_reject_non_jumia_url():
    response = client.post("/api/competitor-products/", json={
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": "https://www.amazon.com/test-product"
    })
    assert response.status_code == 400
    assert "Only Jumia URLs are supported" in response.json()["detail"]


def test_accept_jumia_url():
    response = client.post("/api/competitor-products/", json={
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": "https://www.jumia.co.ke/test-product-123.html"
    })
    assert response.status_code == 200

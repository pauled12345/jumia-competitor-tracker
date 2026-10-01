"""Tests for error handling."""
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


def test_invalid_product_id():
    response = client.post("/api/competitor-products/", json={
        "product_id": "invalid",
        "competitor_id": 1,
        "competitor_product_url": "https://www.jumia.co.ke/test.html"
    })
    assert response.status_code == 422


def test_missing_fields():
    response = client.post("/api/competitor-products/", json={})
    assert response.status_code == 422


def test_scrape_nonexistent():
    response = client.post("/api/scrape/99999")
    assert response.status_code == 404

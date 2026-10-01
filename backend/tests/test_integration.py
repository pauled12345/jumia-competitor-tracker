"""Integration tests for the full workflow."""
import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, engine, Base
from models import Competitor, Product, CompetitorProduct

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Seed minimal data
    db = SessionLocal()
    competitor = Competitor(name="Jumia", platform="jumia", url="https://www.jumia.co.ke")
    product = Product(user_id=1, name="Test Phone", category="phones")
    db.add_all([competitor, product])
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_add_and_list_product():
    # Add a competitor product
    response = client.post("/api/competitor-products/", json={
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": "https://www.jumia.co.ke/test-product-123.html"
    })
    assert response.status_code == 200

    # List products
    response = client.get("/api/competitor-products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["competitor_product_url"] == "https://www.jumia.co.ke/test-product-123.html"


def test_duplicate_product_rejected():
    url = "https://www.jumia.co.ke/test-product-123.html"
    client.post("/api/competitor-products/", json={
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": url
    })
    response = client.post("/api/competitor-products/", json={
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": url
    })
    assert response.status_code == 400

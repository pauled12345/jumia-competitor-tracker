"""Tests for full competitor product lifecycle."""
import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, engine, Base
from models import Competitor, Product, CompetitorProduct, PriceHistory

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    competitor = Competitor(name="Jumia", platform="jumia", url="https://www.jumia.co.ke")
    product = Product(user_id=1, name="Test Phone", category="phones")
    db.add_all([competitor, product])
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_full_lifecycle():
    # 1. Add product
    response = client.post("/api/competitor-products/", json={
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": "https://www.jumia.co.ke/test-product-123.html"
    })
    assert response.status_code == 200
    product_id = response.json()["id"]

    # 2. List products
    response = client.get("/api/competitor-products/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # 3. Get stats
    response = client.get("/api/stats/")
    assert response.status_code == 200
    assert response.json()["total_products_tracked"] == 1

    # 4. Try to add duplicate
    response = client.post("/api/competitor-products/", json={
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": "https://www.jumia.co.ke/test-product-123.html"
    })
    assert response.status_code == 400

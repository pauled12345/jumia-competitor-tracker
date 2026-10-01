"""Tests for concurrent request handling."""
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


def test_multiple_products():
    urls = [
        "https://www.jumia.co.ke/product-1.html",
        "https://www.jumia.co.ke/product-2.html",
        "https://www.jumia.co.ke/product-3.html",
    ]
    for url in urls:
        response = client.post("/api/competitor-products/", json={
            "product_id": 1,
            "competitor_id": 1,
            "competitor_product_url": url
        })
        assert response.status_code == 200

    response = client.get("/api/competitor-products/")
    assert len(response.json()) == 3

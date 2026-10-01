"""Tests for performance considerations."""
import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, engine, Base
from models import Competitor, Product, CompetitorProduct

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


def test_list_products_performance():
    # Add multiple products
    for i in range(10):
        client.post("/api/competitor-products/", json={
            "product_id": 1,
            "competitor_id": 1,
            "competitor_product_url": f"https://www.jumia.co.ke/product-{i}.html"
        })

    response = client.get("/api/competitor-products/")
    assert response.status_code == 200
    assert len(response.json()) == 10

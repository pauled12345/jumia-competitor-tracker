"""Tests for scrape endpoint."""
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

    cp = CompetitorProduct(
        product_id=product.id,
        competitor_id=competitor.id,
        competitor_product_url="https://www.jumia.co.ke/test-123.html"
    )
    db.add(cp)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_scrape_nonexistent_product():
    response = client.post("/api/scrape/9999")
    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]


def test_scrape_all_empty():
    # No products added in this test
    response = client.post("/api/scrape-all/")
    assert response.status_code == 200
    data = response.json()
    assert data["scraped"] == 0

"""Tests for stats endpoint."""
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

    price = PriceHistory(
        competitor_product_id=cp.id,
        price=15000.0,
        currency="KES",
        in_stock=True
    )
    db.add(price)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_stats_returns_correct_counts():
    response = client.get("/api/stats/")
    assert response.status_code == 200
    data = response.json()
    assert data["total_products_tracked"] == 1
    assert data["total_competitors"] == 1
    assert data["total_price_snapshots"] == 1
    assert len(data["recent_updates"]) == 1

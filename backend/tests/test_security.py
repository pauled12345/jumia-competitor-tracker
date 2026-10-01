"""Tests for security considerations."""
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


def test_sql_injection_attempt():
    # Attempt SQL injection in URL field
    response = client.post("/api/competitor-products/", json={
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": "https://www.jumia.co.ke/test'; DROP TABLE users;--.html"
    })
    # Should either succeed (and be stored safely) or fail validation
    assert response.status_code in [200, 400, 422]


def test_xss_attempt_in_url():
    response = client.post("/api/competitor-products/", json={
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": "https://www.jumia.co.ke/<script>alert('xss')</script>.html"
    })
    # Should be stored safely (SQLAlchemy handles escaping)
    assert response.status_code in [200, 400, 422]

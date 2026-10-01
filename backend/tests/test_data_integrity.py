"""Tests for data integrity."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Competitor, Product, CompetitorProduct, PriceHistory


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_cascade_delete_behavior(db_session):
    # Setup
    product = Product(user_id=1, name="Test", category="phones")
    competitor = Competitor(name="Store", platform="jumia", url="https://jumia.co.ke")
    db_session.add_all([product, competitor])
    db_session.commit()

    cp = CompetitorProduct(
        product_id=product.id,
        competitor_id=competitor.id,
        competitor_product_url="https://www.jumia.co.ke/test-123.html"
    )
    db_session.add(cp)
    db_session.commit()

    price = PriceHistory(
        competitor_product_id=cp.id,
        price=15000.0,
        currency="KES",
        in_stock=True
    )
    db_session.add(price)
    db_session.commit()

    # Verify data exists
    assert db_session.query(CompetitorProduct).count() == 1
    assert db_session.query(PriceHistory).count() == 1

    # Delete competitor product
    db_session.delete(cp)
    db_session.commit()

    # Verify price history still exists (no cascade)
    assert db_session.query(PriceHistory).count() == 1

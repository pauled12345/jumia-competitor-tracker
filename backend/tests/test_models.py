"""Tests for database models."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import User, Competitor, Product, CompetitorProduct, PriceHistory


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_competitor(db_session):
    competitor = Competitor(name="Test Store", platform="jumia", url="https://www.jumia.co.ke")
    db_session.add(competitor)
    db_session.commit()
    assert competitor.id is not None


def test_create_product(db_session):
    product = Product(user_id=1, name="Test Product", category="phones")
    db_session.add(product)
    db_session.commit()
    assert product.id is not None


def test_create_price_history(db_session):
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
    assert price.id is not None

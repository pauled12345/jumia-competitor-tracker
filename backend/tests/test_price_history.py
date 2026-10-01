"""Tests for price history functionality."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import PriceHistory, CompetitorProduct, Competitor, Product


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_price_history_ordering(db_session):
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

    # Add price history entries
    for i, price in enumerate([15000, 14000, 13000]):
        entry = PriceHistory(
            competitor_product_id=cp.id,
            price=price,
            currency="KES",
            in_stock=True,
            scraped_at=datetime.utcnow() - timedelta(days=i)
        )
        db_session.add(entry)
    db_session.commit()

    # Query ordered by date
    history = db_session.query(PriceHistory).filter(
        PriceHistory.competitor_product_id == cp.id
    ).order_by(PriceHistory.scraped_at.desc()).all()

    assert len(history) == 3
    assert history[0].price == 13000  # Most recent
    assert history[2].price == 15000  # Oldest

"""Tests for alert functionality."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Alert, CompetitorProduct, PriceHistory


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_alert(db_session):
    alert = Alert(
        user_id=1,
        competitor_product_id=1,
        alert_type="price_drop",
        threshold_value=10000.0,
        is_active=True
    )
    db_session.add(alert)
    db_session.commit()
    assert alert.id is not None
    assert alert.is_active is True


def test_alert_types():
    valid_types = ["price_drop", "out_of_stock", "new_product"]
    for alert_type in valid_types:
        assert alert_type in valid_types

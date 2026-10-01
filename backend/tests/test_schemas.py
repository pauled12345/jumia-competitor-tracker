"""Tests for Pydantic schemas."""
import pytest
from pydantic import ValidationError
from schemas import CompetitorProductCreate, ScrapedProduct


def test_competitor_product_create_valid():
    data = {
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": "https://www.jumia.co.ke/test-123.html"
    }
    product = CompetitorProductCreate(**data)
    assert product.product_id == 1
    assert product.competitor_id == 1


def test_competitor_product_create_invalid_url():
    data = {
        "product_id": 1,
        "competitor_id": 1,
        "competitor_product_url": "not-a-valid-url"
    }
    # Should still create but URL validation happens at API level
    product = CompetitorProductCreate(**data)
    assert product.competitor_product_url == "not-a-valid-url"


def test_scraped_product_valid():
    data = {
        "name": "Test Product",
        "price": 15000.0,
        "currency": "KES",
        "in_stock": True,
        "url": "https://www.jumia.co.ke/test-123.html"
    }
    product = ScrapedProduct(**data)
    assert product.name == "Test Product"
    assert product.price == 15000.0
    assert product.in_stock is True


def test_scraped_product_optional_fields():
    data = {
        "name": "Test Product",
        "price": 15000.0,
        "currency": "KES",
        "in_stock": True,
        "url": "https://www.jumia.co.ke/test-123.html",
        "discount_percent": 15.0,
        "rating": 4.5,
        "seller": "Test Seller"
    }
    product = ScrapedProduct(**data)
    assert product.discount_percent == 15.0
    assert product.rating == 4.5
    assert product.seller == "Test Seller"

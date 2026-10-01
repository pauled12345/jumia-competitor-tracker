"""Tests for the scraper module."""
import pytest
from scraper import normalize_price, scrape_jumia_product


def test_normalize_price():
    assert normalize_price("KSh 14,155") == 14155.0
    assert normalize_price("14,155") == 14155.0
    assert normalize_price("KSh 1,299") == 1299.0
    assert normalize_price("") == 0.0


def test_scrape_jumia_product():
    # This is a basic smoke test - in production you'd mock the fetcher
    url = "https://www.jumia.co.ke/samsung-galaxy-a06-6.7-4gb-ram-64gb-dual-sim-5000mah-black-1yr-wrty-299889399.html"
    result = scrape_jumia_product(url)
    assert "name" in result
    assert "price" in result
    assert "in_stock" in result

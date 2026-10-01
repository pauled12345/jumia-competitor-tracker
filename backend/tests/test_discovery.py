"""Tests for product discovery."""
import pytest
from scraper import discover_jumia_products


def test_discover_returns_list():
    # This is a basic smoke test - in production you'd mock the fetcher
    urls = discover_jumia_products("https://www.jumia.co.ke/phones-tablets/", max_products=3)
    assert isinstance(urls, list)
    assert len(urls) <= 3


def test_discover_filters_non_product_urls():
    urls = discover_jumia_products("https://www.jumia.co.ke/phones-tablets/", max_products=5)
    for url in urls:
        assert url.endswith(".html")
        assert "/customer/account" not in url

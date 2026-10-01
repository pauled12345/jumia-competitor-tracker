"""Tests for category URL mapping."""
import pytest


def test_category_urls_mapping():
    category_urls = {
        "phones": "https://www.jumia.co.ke/phones-tablets/",
        "computing": "https://www.jumia.co.ke/computing/",
        "appliances": "https://www.jumia.co.ke/home-office-appliances/",
    }
    assert "phones" in category_urls
    assert "computing" in category_urls
    assert "appliances" in category_urls
    assert all(url.startswith("https://www.jumia.co.ke/") for url in category_urls.values())


def test_invalid_category():
    category_urls = {
        "phones": "https://www.jumia.co.ke/phones-tablets/",
        "computing": "https://www.jumia.co.ke/computing/",
        "appliances": "https://www.jumia.co.ke/home-office-appliances/",
    }
    assert "invalid" not in category_urls

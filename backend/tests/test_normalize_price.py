"""Tests for price normalization."""
import pytest
from scraper import normalize_price


@pytest.mark.parametrize("input_text,expected", [
    ("KSh 14,155", 14155.0),
    ("14,155", 14155.0),
    ("KSh 1,299", 1299.0),
    ("KSh 999", 999.0),
    ("KSh 1,000,000", 1000000.0),
    ("", 0.0),
    ("KSh 0", 0.0),
    ("Free", 0.0),
    ("KSh 14,155.50", 14155.5),
])
def test_normalize_price(input_text, expected):
    assert normalize_price(input_text) == expected

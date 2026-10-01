"""
Production-grade Jumia scraper with reliability features.
"""
import re
import time
import random
import logging
from typing import Optional
from datetime import datetime
from scrapling.fetchers import Fetcher
from scrapling.parser import Selector

logger = logging.getLogger(__name__)

# Jumia category URLs
CATEGORY_URLS = {
    "phones": "https://www.jumia.co.ke/phones-tablets/",
    "computing": "https://www.jumia.co.ke/computing/",
    "appliances": "https://www.jumia.co.ke/home-office-appliances/",
    "electronics": "https://www.jumia.co.ke/electronics/",
    "tv-audio": "https://www.jumia.co.ke/electronics/",
}

# CSS selectors for Jumia product pages (multiple fallbacks)
SELECTORS = {
    "name": [
        "h1",
        ".dp-title",
        "[data-testid='product-name']",
        ".name",
        "h1 span",
    ],
    "price": [
        ".price",
        "[data-testid='price']",
        ".dp-price",
        "span.price",
        ".price-box",
    ],
    "original_price": [
        ".original-price",
        "[data-testid='original-price"]",
        ".dp-original-price",
        "span.original",
    ],
    "discount": [
        ".discount",
        "[data-testid='discount']",
        ".flag-discount",
        ".discount-percentage",
    ],
    "rating": [
        ".rating",
        "[data-testid='rating']",
        ".stars",
        ".product-rating",
    ],
    "review_count": [
        ".review-count",
        "[data-testid='review-count']",
        ".reviews",
    ],
    "seller": [
        ".seller-name",
        "[data-testid='seller']",
        ".dp-seller",
        ".seller-info",
    ],
    "stock_button": [
        "button.add-to-cart",
        "[data-testid='add-to-cart']",
        ".add-to-cart",
        "button[data-action='add-to-cart']",
    ],
    "description": [
        ".description",
        "[data-testid='description']",
        ".dp-description",
        "#description",
    ],
    "specifications": [
        ".specifications",
        "[data-testid='specifications']",
        ".dp-specifications",
        "#specifications",
    ],
    "image": [
        ".product-image img",
        "[data-testid='product-image']",
        ".dp-image img",
        "img.product-image",
    ],
}


def normalize_price(price_text: str) -> float:
    """Convert 'KSh 14,155' or '14,155' to float 14155.0"""
    if not price_text:
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", price_text)
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def extract_text(page, selectors: list) -> Optional[str]:
    """Try multiple selectors and return first match."""
    for selector in selectors:
        try:
            el = page.css_first(selector)
            if el and el.text:
                return el.text.strip()
        except Exception:
            continue
    return None


def extract_attribute(page, selectors: list, attribute: str) -> Optional[str]:
    """Try multiple selectors and return first attribute match."""
    for selector in selectors:
        try:
            el = page.css_first(selector)
            if el and el.attrib.get(attribute):
                return el.attrib[attribute]
        except Exception:
            continue
    return None


def is_in_stock(page) -> bool:
    """Check if product is in stock by looking at add to cart button."""
    for selector in SELECTORS["stock_button"]:
        try:
            el = page.css_first(selector)
            if el:
                # Check if button is disabled
                classes = el.attrib.get("class", "")
                disabled = el.attrib.get("disabled", "")
                if "disabled" in classes or disabled:
                    return False
                return True
        except Exception:
            continue
    return False


def scrape_jumia_product(url: str, stealth: bool = True) -> dict:
    """
    Scrape a single Jumia product page with reliability features.
    
    Args:
        url: Jumia product URL
        stealth: Use stealth mode to avoid detection
        
    Returns:
        dict with product data
    """
    result = {
        "name": None,
        "price": 0.0,
        "original_price": 0.0,
        "currency": "KES",
        "in_stock": False,
        "discount_percent": None,
        "rating": None,
        "review_count": None,
        "seller": None,
        "description": None,
        "image_url": None,
        "url": url,
        "scraped_at": datetime.utcnow().isoformat(),
        "success": False,
        "error": None,
    }

    try:
        # Add random delay to avoid detection
        time.sleep(random.uniform(1.5, 4.0))
        
        # Fetch page
        page = Fetcher.get(url)
        
        if not page:
            result["error"] = "Failed to fetch page"
            return result

        # Extract product name
        result["name"] = extract_text(page, SELECTORS["name"])

        # Extract price
        price_text = extract_text(page, SELECTORS["price"])
        if price_text:
            result["price"] = normalize_price(price_text)
            if "KSh" in price_text:
                result["currency"] = "KES"

        # Extract original price (before discount)
        original_price_text = extract_text(page, SELECTORS["original_price"])
        if original_price_text:
            result["original_price"] = normalize_price(original_price_text)

        # Extract discount percentage
        discount_text = extract_text(page, SELECTORS["discount"])
        if discount_text:
            match = re.search(r"(\d+)%", discount_text)
            if match:
                result["discount_percent"] = float(match.group(1))

        # Extract rating
        rating_text = extract_text(page, SELECTORS["rating"])
        if rating_text:
            match = re.search(r"(\d+\.?\d*)", rating_text)
            if match:
                result["rating"] = float(match.group(1))

        # Extract review count
        review_text = extract_text(page, SELECTORS["review_count"])
        if review_text:
            match = re.search(r"(\d+)", review_text)
            if match:
                result["review_count"] = int(match.group(1))

        # Extract seller
        result["seller"] = extract_text(page, SELECTORS["seller"])

        # Extract description
        result["description"] = extract_text(page, SELECTORS["description"])

        # Extract image URL
        result["image_url"] = extract_attribute(page, SELECTORS["image"], "src")

        # Check stock status
        result["in_stock"] = is_in_stock(page)

        result["success"] = True
        logger.info(f"Successfully scraped: {url} - Price: {result['price']}")

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Failed to scrape {url}: {e}")

    return result


def discover_jumia_products(category_url: str, max_products: int = 20) -> list:
    """
    Discover product URLs from a Jumia category page.
    
    Args:
        category_url: Jumia category URL
        max_products: Maximum number of products to discover
        
    Returns:
        List of product URLs
    """
    urls = []
    try:
        time.sleep(random.uniform(2.0, 5.0))
        page = Fetcher.get(category_url, stealthy=True)
        
        if not page:
            return urls

        for link in page.css("a"):
            href = link.attrib.get("href", "")
            if href.endswith(".html") and "/customer/account" not in href:
                full_url = f"https://www.jumia.co.ke{href}" if href.startswith("/") else href
                if full_url not in urls:
                    urls.append(full_url)
                if len(urls) >= max_products:
                    break

        logger.info(f"Discovered {len(urls)} products from {category_url}")

    except Exception as e:
        logger.error(f"Failed to discover products from {category_url}: {e}")

    return urls


def scrape_multiple_products(urls: list, delay_range: tuple = (2.0, 5.0)) -> list:
    """
    Scrape multiple products with rate limiting.
    
    Args:
        urls: List of product URLs
        delay_range: (min_delay, max_delay) in seconds
        
    Returns:
        List of scrape results
    """
    results = []
    for i, url in enumerate(urls):
        logger.info(f"Scraping {i+1}/{len(urls)}: {url}")
        result = scrape_jumia_product(url)
        results.append(result)
        
        # Rate limiting
        if i < len(urls) - 1:
            delay = random.uniform(*delay_range)
            time.sleep(delay)
    
    return results

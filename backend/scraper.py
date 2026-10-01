import re
import time
import random
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

CATEGORY_URLS = {
    "phones": "https://www.jumia.co.ke/phones-tablets/",
    "computing": "https://www.jumia.co.ke/computing/",
    "appliances": "https://www.jumia.co.ke/home-office-appliances/",
    "electronics": "https://www.jumia.co.ke/electronics/",
}


def normalize_price(price_text: str) -> float:
    if not price_text:
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", price_text)
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def scrape_jumia_product(url: str) -> dict:
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
        "url": url,
        "scraped_at": datetime.utcnow().isoformat(),
        "success": False,
        "error": None,
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path=r"C:\Users\Paule\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe",
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(8)

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            # Name
            h1 = soup.find("h1")
            if h1:
                result["name"] = h1.text.strip()

            # Price - try multiple selectors
            for sel in [".price", "[data-testid='price']", ".dp-price", "span.price", ".price-box"]:
                price_el = soup.select_one(sel)
                if price_el:
                    result["price"] = normalize_price(price_el.text.strip())
                    break

            # Original price
            orig_el = soup.select_one(".original-price")
            if orig_el:
                result["original_price"] = normalize_price(orig_el.text.strip())

            # Discount
            disc_el = soup.select_one(".discount")
            if disc_el:
                match = re.search(r"(\d+)%", disc_el.text)
                if match:
                    result["discount_percent"] = float(match.group(1))

            # Stock
            add_to_cart = soup.select_one("button.add-to-cart")
            result["in_stock"] = add_to_cart is not None

            # Rating
            rating_el = soup.select_one(".rating")
            if rating_el:
                match = re.search(r"(\d+\.?\d*)", rating_el.text)
                if match:
                    result["rating"] = float(match.group(1))

            # Seller
            seller_el = soup.select_one(".seller-name")
            if seller_el:
                result["seller"] = seller_el.text.strip()

            browser.close()

        result["success"] = True
        logger.info(f"Scraped {url}: {result['name']} - {result['price']}")

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Failed to scrape {url}: {e}")

    return result


def discover_jumia_products(category_url: str, max_products: int = 20) -> list:
    urls = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path=r"C:\Users\Paule\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe",
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            )
            page = context.new_page()
            page.goto(category_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)

            links = page.query_selector_all("a")
            for link in links:
                href = link.get_attribute("href") or ""
                if href.endswith(".html") and "/customer/account" not in href:
                    full_url = f"https://www.jumia.co.ke{href}" if href.startswith("/") else href
                    if full_url not in urls:
                        urls.append(full_url)
                    if len(urls) >= max_products:
                        break

            browser.close()
        logger.info(f"Discovered {len(urls)} products from {category_url}")

    except Exception as e:
        logger.error(f"Failed to discover products from {category_url}: {e}")

    return urls

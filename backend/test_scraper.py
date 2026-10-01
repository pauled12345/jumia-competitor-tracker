"""Quick test to verify the scraper works."""
from scraper import scrape_jumia_product, discover_jumia_products

# Test with a real Jumia product URL
test_url = "https://www.jumia.co.ke/samsung-galaxy-a06-6.7-4gb-ram-64gb-dual-sim-5000mah-black-1yr-wrty-299889399.html"

print("Testing scraper with:", test_url)
print("-" * 50)

result = scrape_jumia_product(test_url)

for key, value in result.items():
    print(f"{key}: {value}")

print("\n" + "=" * 50)
print("Testing product discovery...")
print("-" * 50)

# Test discovery
urls = discover_jumia_products("https://www.jumia.co.ke/phones-tablets/", max_products=3)
for url in urls:
    print(f"Found: {url}")

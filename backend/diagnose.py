from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path=r"C:\Users\Paule\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe",
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    )
    page = context.new_page()
    page.goto(
        "https://www.jumia.co.ke/samsung-galaxy-a06-6.7-4gb-ram-64gb-dual-sim-5000mah-black-1yr-wrty-299889399.html",
        wait_until="domcontentloaded",
        timeout=60000,
    )
    time.sleep(8)
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Find elements containing KSh and show their hierarchy
    ksh_elements = soup.find_all(string=lambda text: text and "KSh" in text)
    print(f"Elements with KSh: {len(ksh_elements)}")
    for i, el in enumerate(ksh_elements[:3]):
        print(f"\n--- Element {i+1} ---")
        print(f"Text: {el.strip()[:50]}")
        print(f"Parent: {el.parent.name} class={el.parent.get('class')}")
        print(f"Grandparent: {el.parent.parent.name} class={el.parent.parent.get('class')}")
        print(f"Great-grandparent: {el.parent.parent.parent.name} class={el.parent.parent.parent.get('class')}")

    # Also check for common Jumia selectors
    print("\n--- Checking common selectors ---")
    for sel in [".dp-price", ".price-box", "[class*='price']", "[class*='Price']"]:
        elements = soup.select(sel)
        if elements:
            print(f"{sel}: {len(elements)} elements")
            for el in elements[:2]:
                print(f"  Text: {el.text.strip()[:50]}")

    browser.close()

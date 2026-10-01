"""Seed the database with sample competitors and products."""
from database import SessionLocal, engine, Base
from models import Competitor, Product, CompetitorProduct

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create sample competitors
competitors = [
    Competitor(name="Jumia Official Store", platform="jumia", url="https://www.jumia.co.ke"),
    Competitor(name="Phone House", platform="jumia", url="https://www.jumia.co.ke/phone-house/"),
    Competitor(name="Computers & Accessories", platform="jumia", url="https://www.jumia.co.ke/computing/"),
]

for c in competitors:
    db.add(c)
db.commit()

# Create sample products
products = [
    Product(user_id=1, name="Samsung Galaxy A16", category="phones"),
    Product(user_id=1, name="Lenovo Laptop", category="computing"),
    Product(user_id=1, name="Ramtons Steam Iron", category="appliances"),
]

for p in products:
    db.add(p)
db.commit()

# Create sample competitor products (real Jumia URLs from our research)
sample_urls = [
    (1, 1, "https://www.jumia.co.ke/samsung-galaxy-a06-6.7-4gb-ram-64gb-dual-sim-5000mah-black-1yr-wrty-299889399.html"),
    (1, 2, "https://www.jumia.co.ke/samsung-galaxy-a16-4gb-ram-128gb-rom-6.7-hd-android-1450mp-camera-battery-5000mah-black-327756395.html"),
    (2, 1, "https://www.jumia.co.ke/lenovo-m8-4th-gen-8-inch-android-tablet-hd-display-4gb-ram-64gb-storage-wifi-4g-lte-android-13-5100mah-battery-kids-mode-dual-speakers-reading-mode-expandable-storage-327763001.html"),
    (3, 1, "https://www.jumia.co.ke/ramtons-steam-iron-non-stick-sole-plate-rm694-1yr-wrty-326563920.html"),
]

for product_id, competitor_id, url in sample_urls:
    cp = CompetitorProduct(
        product_id=product_id,
        competitor_id=competitor_id,
        competitor_product_url=url,
    )
    db.add(cp)

db.commit()
print("Database seeded successfully!")
print(f"Competitors: {db.query(Competitor).count()}")
print(f"Products: {db.query(Product).count()}")
print(f"Competitor Products: {db.query(CompetitorProduct).count()}")
db.close()

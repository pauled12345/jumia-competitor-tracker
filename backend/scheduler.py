"""Background scheduler for automated scraping."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import SessionLocal
from models import CompetitorProduct, PriceHistory
from scraper import scrape_jumia_product
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def scrape_all_tracked_products():
    """Job to scrape all tracked products."""
    db = SessionLocal()
    try:
        products = db.query(CompetitorProduct).filter(
            CompetitorProduct.is_active == True
        ).all()

        logger.info(f"Starting scheduled scrape of {len(products)} products")

        for cp in products:
            try:
                result = scrape_jumia_product(cp.competitor_product_url)
                if result["price"] > 0:
                    price_entry = PriceHistory(
                        competitor_product_id=cp.id,
                        price=result["price"],
                        currency=result["currency"],
                        in_stock=result["in_stock"],
                    )
                    db.add(price_entry)
                    cp.last_scraped_at = datetime.utcnow()
                    db.commit()
                    logger.info(f"Scraped {cp.competitor_product_url}: {result['price']}")
            except Exception as e:
                logger.error(f"Failed to scrape {cp.competitor_product_url}: {e}")

        logger.info("Scheduled scrape completed")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler."""
    scheduler.add_job(
        scrape_all_tracked_products,
        trigger=IntervalTrigger(hours=6),
        id="scrape_all",
        name="Scrape all tracked products",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started - scraping every 6 hours")


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler stopped")

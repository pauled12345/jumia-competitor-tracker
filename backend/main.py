from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import engine, get_db, Base
from models import Competitor, Product, CompetitorProduct, PriceHistory, Alert
from schemas import CompetitorProductCreate, CompetitorProductResponse, PriceHistoryResponse, ScrapedProduct
from scraper import scrape_jumia_product, discover_jumia_products

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jumia Competitor Tracker", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Competitor Products ---

@app.post("/api/competitor-products/", response_model=CompetitorProductResponse)
def add_competitor_product(data: CompetitorProductCreate, db: Session = Depends(get_db)):
    """Add a competitor product URL to track."""
    # Validate URL is a Jumia product page
    if "jumia.co.ke" not in data.competitor_product_url:
        raise HTTPException(status_code=400, detail="Only Jumia URLs are supported")

    # Check if already exists
    existing = db.query(CompetitorProduct).filter(
        CompetitorProduct.competitor_product_url == data.competitor_product_url
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="This product is already being tracked")

    cp = CompetitorProduct(**data.model_dump())
    db.add(cp)
    db.commit()
    db.refresh(cp)
    return cp


@app.get("/api/competitor-products/", response_model=List[CompetitorProductResponse])
def list_competitor_products(db: Session = Depends(get_db)):
    """List all tracked competitor products."""
    return db.query(CompetitorProduct).filter(CompetitorProduct.is_active == True).all()


@app.post("/api/scrape/{competitor_product_id}", response_model=ScrapedProduct)
def scrape_product(competitor_product_id: int, db: Session = Depends(get_db)):
    """Manually trigger a scrape for a specific product."""
    cp = db.query(CompetitorProduct).filter(CompetitorProduct.id == competitor_product_id).first()
    if not cp:
        raise HTTPException(status_code=404, detail="Product not found")

    result = scrape_jumia_product(cp.competitor_product_url)

    # Store price history
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

    return result


@app.post("/api/scrape-all/")
def scrape_all_products(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger scraping for all tracked products."""
    products = db.query(CompetitorProduct).filter(CompetitorProduct.is_active == True).all()

    results = []
    for cp in products:
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
        results.append(result)

    db.commit()
    return {"scraped": len(results), "results": results}


# --- Price History ---

@app.get("/api/price-history/{competitor_product_id}", response_model=List[PriceHistoryResponse])
def get_price_history(competitor_product_id: int, db: Session = Depends(get_db)):
    """Get price history for a specific product."""
    return db.query(PriceHistory).filter(
        PriceHistory.competitor_product_id == competitor_product_id
    ).order_by(PriceHistory.scraped_at.desc()).all()


# --- Discovery ---

@app.get("/api/discover/")
def discover_products(category: str = "phones", max_products: int = 10):
    """Discover product URLs from a Jumia category."""
    category_urls = {
        "phones": "https://www.jumia.co.ke/phones-tablets/",
        "computing": "https://www.jumia.co.ke/computing/",
        "appliances": "https://www.jumia.co.ke/home-office-appliances/",
    }

    url = category_urls.get(category)
    if not url:
        raise HTTPException(status_code=400, detail=f"Unknown category. Choose from: {list(category_urls.keys())}")

    products = discover_jumia_products(url, max_products)
    return {"category": category, "products_found": len(products), "urls": products}


# --- Dashboard Stats ---

@app.get("/api/stats/")
def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    total_products = db.query(CompetitorProduct).filter(CompetitorProduct.is_active == True).count()
    total_competitors = db.query(Competitor).count()
    total_price_entries = db.query(PriceHistory).count()
    recent_prices = db.query(PriceHistory).order_by(PriceHistory.scraped_at.desc()).limit(5).all()

    return {
        "total_products_tracked": total_products,
        "total_competitors": total_competitors,
        "total_price_snapshots": total_price_entries,
        "recent_updates": [
            {
                "product_id": p.competitor_product_id,
                "price": p.price,
                "in_stock": p.in_stock,
                "scraped_at": p.scraped_at,
            }
            for p in recent_prices
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

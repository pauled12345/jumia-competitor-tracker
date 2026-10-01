"""
Production-ready FastAPI application for Jumia Price Scout.
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, HttpUrl
import uvicorn
import logging

from database import engine, get_db, Base
from models import User, Competitor, Product, CompetitorProduct, PriceHistory, Alert
from improved_scraper import scrape_jumia_product, discover_jumia_products, CATEGORY_URLS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Jumia Price Scout",
    description="Competitive intelligence platform for Jumia sellers",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]),
)

# Mount static files for dashboard
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Pydantic Schemas ---

class ProductCreate(BaseModel):
    name: str
    category: str
    sku: Optional[str] = None


class CompetitorCreate(BaseModel):
    name: str
    platform: str = "jumia"
    url: HttpUrl


class CompetitorProductCreate(BaseModel):
    product_id: int
    competitor_id: int
    competitor_product_url: HttpUrl


class AlertCreate(BaseModel):
    competitor_product_id: int
    alert_type: str  # price_drop, out_of_stock, new_product
    threshold_value: Optional[float] = None


class PriceHistoryResponse(BaseModel):
    id: int
    competitor_product_id: int
    price: float
    currency: str
    in_stock: bool
    scraped_at: datetime

    class Config:
        from_attributes = True


class CompetitorProductResponse(BaseModel):
    id: int
    product_id: int
    competitor_id: int
    competitor_product_url: str
    last_scraped_at: Optional[datetime] = None
    is_active: bool
    latest_price: Optional[float] = None
    latest_stock: Optional[bool] = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_products: int
    total_competitors: int
    total_price_snapshots: int
    active_alerts: int
    recent_changes: List[dict]


# --- API Endpoints ---

@app.get("/")
def root():
    return {"message": "Jumia Price Scout API", "version": "2.0.0"}


@app.get("/api/stats/", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    total_products = db.query(CompetitorProduct).filter(CompetitorProduct.is_active == True).count()
    total_competitors = db.query(Competitor).count()
    total_snapshots = db.query(PriceHistory).count()
    active_alerts = db.query(Alert).filter(Alert.is_active == True).count()

    # Get recent price changes (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(hours=24)
    recent = db.query(PriceHistory).filter(
        PriceHistory.scraped_at >= yesterday
    ).order_by(PriceHistory.scraped_at.desc()).limit(10).all()

    return DashboardStats(
        total_products=total_products,
        total_competitors=total_competitors,
        total_price_snapshots=total_snapshots,
        active_alerts=active_alerts,
        recent_changes=[
            {
                "product_id": r.competitor_product_id,
                "price": r.price,
                "in_stock": r.in_stock,
                "scraped_at": r.scraped_at,
            }
            for r in recent
        ],
    )


@app.post("/api/products/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product to track."""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/api/products/")
def list_products(db: Session = Depends(get_db)):
    """List all products."""
    return db.query(Product).all()


@app.post("/api/competitors/")
def create_competitor(competitor: CompetitorCreate, db: Session = Depends(get_db)):
    """Create a new competitor."""
    db_competitor = Competitor(**competitor.model_dump())
    db.add(db_competitor)
    db.commit()
    db.refresh(db_competitor)
    return db_competitor


@app.get("/api/competitors/")
def list_competitors(db: Session = Depends(get_db)):
    """List all competitors."""
    return db.query(Competitor).all()


@app.post("/api/competitor-products/", response_model=CompetitorProductResponse)
def add_competitor_product(data: CompetitorProductCreate, db: Session = Depends(get_db)):
    """Add a competitor product URL to track."""
    url_str = str(data.competitor_product_url)
    
    if "jumia.co.ke" not in url_str:
        raise HTTPException(status_code=400, detail="Only Jumia URLs are supported")

    existing = db.query(CompetitorProduct).filter(
        CompetitorProduct.competitor_product_url == url_str
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="This product is already being tracked")

    cp = CompetitorProduct(
        product_id=data.product_id,
        competitor_id=data.competitor_id,
        competitor_product_url=url_str,
    )
    db.add(cp)
    db.commit()
    db.refresh(cp)
    return cp


@app.get("/api/competitor-products/", response_model=List[CompetitorProductResponse])
def list_competitor_products(db: Session = Depends(get_db)):
    """List all tracked competitor products with latest price."""
    products = db.query(CompetitorProduct).filter(CompetitorProduct.is_active == True).all()
    
    result = []
    for cp in products:
        latest = db.query(PriceHistory).filter(
            PriceHistory.competitor_product_id == cp.id
        ).order_by(PriceHistory.scraped_at.desc()).first()
        
        result.append(CompetitorProductResponse(
            id=cp.id,
            product_id=cp.product_id,
            competitor_id=cp.competitor_id,
            competitor_product_url=cp.competitor_product_url,
            last_scraped_at=cp.last_scraped_at,
            is_active=cp.is_active,
            latest_price=latest.price if latest else None,
            latest_stock=latest.in_stock if latest else None,
        ))
    
    return result


@app.post("/api/scrape/{competitor_product_id}")
def scrape_product(competitor_product_id: int, db: Session = Depends(get_db)):
    """Manually trigger a scrape for a specific product."""
    cp = db.query(CompetitorProduct).filter(CompetitorProduct.id == competitor_product_id).first()
    if not cp:
        raise HTTPException(status_code=404, detail="Product not found")

    result = scrape_jumia_product(cp.competitor_product_url)

    if result["success"] and result["price"] > 0:
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
        if result["success"] and result["price"] > 0:
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
    return {"scraped": len(results), "successful": sum(1 for r in results if r["success"]), "results": results}


@app.get("/api/price-history/{competitor_product_id}", response_model=List[PriceHistoryResponse])
def get_price_history(competitor_product_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Get price history for a specific product."""
    since = datetime.utcnow() - timedelta(days=days)
    return db.query(PriceHistory).filter(
        PriceHistory.competitor_product_id == competitor_product_id,
        PriceHistory.scraped_at >= since,
    ).order_by(PriceHistory.scraped_at.desc()).all()


@app.get("/api/discover/")
def discover_products(category: str = "phones", max_products: int = 10):
    """Discover product URLs from a Jumia category."""
    category_url = CATEGORY_URLS.get(category)
    if not category_url:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown category. Choose from: {list(CATEGORY_URLS.keys())}"
        )

    products = discover_jumia_products(category_url, max_products)
    return {"category": category, "products_found": len(products), "urls": products}


@app.post("/api/alerts/")
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert."""
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@app.get("/api/alerts/")
def list_alerts(db: Session = Depends(get_db)):
    """List all active alerts."""
    return db.query(Alert).filter(Alert.is_active == True).all()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

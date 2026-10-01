from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CompetitorProductCreate(BaseModel):
    product_id: int
    competitor_id: int
    competitor_product_url: str


class CompetitorProductResponse(BaseModel):
    id: int
    product_id: int
    competitor_id: int
    competitor_product_url: str
    last_scraped_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    id: int
    competitor_product_id: int
    price: float
    currency: str
    in_stock: bool
    scraped_at: datetime

    class Config:
        from_attributes = True


class ScrapedProduct(BaseModel):
    name: str
    price: float
    currency: str
    in_stock: bool
    discount_percent: Optional[float] = None
    rating: Optional[float] = None
    seller: Optional[str] = None
    url: str

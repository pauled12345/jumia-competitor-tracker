# Jumia Competitor Tracker

A competitive intelligence platform for Jumia Kenya sellers. Track competitor prices, stock levels, and market trends for phones, computers, and home appliances.

## Features

- **Product Discovery**: Automatically find products from Jumia categories
- **Price Tracking**: Scheduled scraping of competitor prices
- **Stock Monitoring**: Track when competitors go out of stock
- **Price History**: View price trends over time
- **Multi-Category**: Phones, Computing, Home Appliances

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy
- **Scraping**: Scrapling (stealth mode for anti-bot bypass)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Simple HTML/JS dashboard

## Quick Start

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Run the server
python main.py

# 3. Open dashboard
# Go to http://localhost:8000/static/dashboard.html
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/competitor-products/` | POST | Add a product to track |
| `/api/competitor-products/` | GET | List tracked products |
| `/api/scrape/{id}` | POST | Scrape a single product |
| `/api/scrape-all/` | POST | Scrape all tracked products |
| `/api/price-history/{id}` | GET | Get price history |
| `/api/discover/` | GET | Discover products by category |
| `/api/stats/` | GET | Dashboard statistics |

## Project Structure

```
jumia-competitor-tracker/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── scraper.py        # Scrapling scraper
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database config
│   ├── dashboard.html    # Simple dashboard
│   └── requirements.txt  # Dependencies
└── README.md
```

## Categories Supported

- `phones` - Phones & Tablets
- `computing` - Laptops, Desktops, Accessories
- `appliances` - Home & Office Appliances

## Legal Notice

This tool is for educational purposes. Respect Jumia's robots.txt and terms of service. Use responsibly and do not hammer their servers with requests.

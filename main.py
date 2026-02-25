"""
DUAL PRODUCT BACKEND
===================
1. MarketEdge - Channel Spend Optimization
2. PriceGenix - Product Price Optimization
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import market_edge, pricegenix
import os
from dotenv import load_dotenv

load_dotenv()


# ==================== FASTAPI APPLICATION ====================

app = FastAPI(
    title="MarketEdge & PriceGenix API",
    description="""
    ## 🚀 Dual Optimization Backend
    
    ### 📊 MarketEdge
    **Channel Spend Optimization** across SEO, Social Media Marketing, and Out-of-Home advertising.
    
    - Maximize Portfolio ROAS
    - Maximize Total GMV  
    - Minimize Total Spend
    
    ### 💰 PriceGenix
    **Product Price Optimization** across 6 brands: Bosch, Haier, IFB, LG, Samsung, Whirlpool.
    
    - Maximize Total GMV
    - Maximize Total Profit
    - Maximize Profit Margin %
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==================== CORS MIDDLEWARE ====================

allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

if not origins:
    origins = ["*"] # Fallback

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== INCLUDE ROUTERS ====================

app.include_router(market_edge.router)
app.include_router(pricegenix.router)


# ==================== ROOT ENDPOINTS ====================

@app.get("/")
async def root():
    """
    API Root - Product Information
    """
    return {
        "message": "MarketEdge & PriceGenix Optimization API",
        "version": "1.0.0",
        "products": {
            "market_edge": {
                "name": "MarketEdge",
                "description": "Channel Spend Optimization",
                "channels": ["SEO", "Social Media Marketing", "Out-of-Home"],
                "base_url": "/api/v1/market-edge",
                "endpoints": [
                    {
                        "path": "/maximize-roas",
                        "objective": "Maximize Portfolio ROAS"
                    },
                    {
                        "path": "/maximize-gmv",
                        "objective": "Maximize Total GMV"
                    },
                    {
                        "path": "/minimize-spend",
                        "objective": "Minimize Total Spend"
                    }
                ]
            },
            "pricegenix": {
                "name": "PriceGenix",
                "description": "Product Price Optimization",
                "brands": ["Bosch", "Haier", "IFB", "LG", "Samsung", "Whirlpool"],
                "base_url": "/api/v1/pricegenix",
                "endpoints": [
                    {
                        "path": "/maximize-gmv",
                        "objective": "Maximize Total GMV"
                    },
                    {
                        "path": "/maximize-profit",
                        "objective": "Maximize Total Profit (₹)"
                    },
                    {
                        "path": "/maximize-profit-percent",
                        "objective": "Maximize Profit Margin %"
                    }
                ]
            }
        },
        "documentation": {
            "swagger_ui": "http://localhost:8000/docs",
            "redoc": "http://localhost:8000/redoc"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health Check - Service Status
    """
    return {
        "status": "healthy",
        "products": {
            "market_edge": {
                "status": "operational",
                "service": "Channel Optimization"
            },
            "pricegenix": {
                "status": "operational",
                "service": "Price Optimization"
            }
        }
    }


# ==================== PRODUCT-SPECIFIC HEALTH CHECKS ====================

@app.get("/market-edge/health")
async def market_edge_health():
    """MarketEdge Service Health"""
    return {
        "product": "MarketEdge",
        "status": "operational",
        "description": "Channel Spend Optimization",
        "channels": 3,
        "endpoints": 3
    }


@app.get("/pricegenix/health")
async def pricegenix_health():
    """PriceGenix Service Health"""
    return {
        "product": "PriceGenix",
        "status": "operational",
        "description": "Product Price Optimization",
        "brands": 6,
        "endpoints": 3
    }


# ==================== STARTUP/SHUTDOWN EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("\n" + "=" * 70)
    print("🚀 DUAL PRODUCT BACKEND STARTED")
    print("=" * 70)
    print("📊 MarketEdge: Channel Optimization")
    print("   └─ Endpoints: /api/v1/market-edge/*")
    print("")
    print("💰 PriceGenix: Price Optimization")
    print("   └─ Endpoints: /api/v1/pricegenix/*")
    print("")
    port = os.getenv("PORT", "8000")
    print(f"📖 Documentation: http://localhost:{port}/docs")
    print("=" * 70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("\n" + "=" * 70)
    print("🛑 BACKEND SHUTTING DOWN")
    print("=" * 70 + "\n")

"""
DUAL PRODUCT BACKEND
===================
1. MarketEdge - Channel Spend Optimization
2. PriceGenix - Product Price Optimization
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import market_edge, pricegenix
from dotenv import load_dotenv

load_dotenv()

# ==================== CORS CONFIGURATION ====================
# Read allowed origins from environment variable (comma-separated)
# Falls back to allowing all origins if not set
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
if _raw_origins.strip() == "*":
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
            "swagger_ui": "/docs",
            "redoc": "/redoc"
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
    print("📖 Documentation: /docs")
    print("=" * 70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("\n" + "=" * 70)
    print("🛑 BACKEND SHUTTING DOWN")
    print("=" * 70 + "\n")


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

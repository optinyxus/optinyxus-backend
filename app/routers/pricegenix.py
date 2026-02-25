"""
PriceGenix API Routes
"""

from fastapi import APIRouter, HTTPException
from app.models.pricegenix_models import PriceGenixRequest, PriceGenixResponse, ErrorResponse
from app.services.pricegenix.maximize_gmv import run_maximize_gmv_optimization
from app.services.pricegenix.maximize_profit import run_maximize_profit_optimization
from app.services.pricegenix.maximize_profit_percent import run_maximize_profit_percent_optimization

router = APIRouter(
    prefix="/api/v1/pricegenix",
    tags=["PriceGenix Optimization"]
)


@router.post("/maximize-gmv", response_model=PriceGenixResponse)
async def maximize_gmv(request: PriceGenixRequest):
    """
    **MAXIMIZE TOTAL GMV (Revenue)**
    
    Optimizes prices across all 6 brands to maximize total revenue while respecting constraints.
    
    **Objective:** max(GMV₁ + GMV₂ + GMV₃ + GMV₄ + GMV₅ + GMV₆)
    """
    try:
        result = run_maximize_gmv_optimization(request.dict())
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": "Internal server error during optimization",
            "details": str(e)
        })


@router.post("/maximize-profit", response_model=PriceGenixResponse)
async def maximize_profit(request: PriceGenixRequest):
    """
    **MAXIMIZE TOTAL PROFIT (₹)**
    
    Optimizes prices across all 6 brands to maximize total profit while respecting constraints.
    
    **Objective:** max(Profit₁ + Profit₂ + Profit₃ + Profit₄ + Profit₅ + Profit₆)
    """
    try:
        result = run_maximize_profit_optimization(request.dict())
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": "Internal server error during optimization",
            "details": str(e)
        })


@router.post("/maximize-profit-percent", response_model=PriceGenixResponse)
async def maximize_profit_percent(request: PriceGenixRequest):
    """
    **MAXIMIZE PORTFOLIO MARGIN %**
    
    Optimizes prices across all 6 brands to maximize portfolio profit margin percentage.
    
    **Objective:** max(Total Profit / Total GMV × 100)
    """
    try:
        result = run_maximize_profit_percent_optimization(request.dict())
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": "Internal server error during optimization",
            "details": str(e)
        })


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "PriceGenix Optimization API",
        "version": "1.0.0"
    }

"""
PriceGenix API Routes
"""

from datetime import datetime, timezone
import json
import traceback
from fastapi import APIRouter, HTTPException, Request
from app.models.pricegenix_models import PriceGenixRequest, PriceGenixResponse
from app.services.pricegenix.maximize_gmv import run_maximize_gmv_optimization
from app.services.pricegenix.maximize_profit import run_maximize_profit_optimization
from app.services.pricegenix.maximize_profit_percent import run_maximize_profit_percent_optimization

router = APIRouter(
    prefix="/api/v1/pricegenix",
    tags=["PriceGenix Optimization"]
)


def _format_json(payload):
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)


def _log_request(endpoint: str, payload):
    print("\n===== REQUEST RECEIVED =====")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Endpoint: {endpoint}")
    print("Payload:")
    print(_format_json(payload))


def _log_response(payload):
    print("\n===== RESPONSE SENT =====")
    print("Processed Result:")
    print(_format_json(payload))
    print("Final Response Payload:")
    print(_format_json(payload))


def _error_payload(error: Exception):
    return {
        "status": "error",
        "message": "Internal server error during optimization",
        "details": str(error)
    }


def _build_request_data(payload: PriceGenixRequest, raw_body):
    """Keep validated fields while preserving table_data needed for dynamic stock."""
    request_data = payload.dict()
    if isinstance(raw_body, dict) and "table_data" in raw_body:
        request_data["table_data"] = raw_body.get("table_data")
    return request_data


@router.post("/maximize-gmv", response_model=PriceGenixResponse)
async def maximize_gmv(request: Request, payload: PriceGenixRequest):
    """
    **MAXIMIZE TOTAL GMV (Revenue)**

    Optimizes prices across all 6 brands to maximize total revenue while respecting constraints.

    **Objective:** max(GMV₁ + GMV₂ + GMV₃ + GMV₄ + GMV₅ + GMV₆)
    """
    endpoint = "/maximize-gmv"
    raw_body = await request.json()
    _log_request(endpoint, raw_body)

    try:
        result = run_maximize_gmv_optimization(_build_request_data(payload, raw_body))
        _log_response(result)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result)

        return result
    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        error_data = _error_payload(e)
        _log_response(error_data)
        raise HTTPException(status_code=500, detail=error_data)


@router.post("/maximize-profit", response_model=PriceGenixResponse)
async def maximize_profit(request: Request, payload: PriceGenixRequest):
    """
    **MAXIMIZE TOTAL PROFIT (₹)**

    Optimizes prices across all 6 brands to maximize total profit while respecting constraints.

    **Objective:** max(Profit₁ + Profit₂ + Profit₃ + Profit₄ + Profit₅ + Profit₆)
    """
    endpoint = "/maximize-profit"
    raw_body = await request.json()
    _log_request(endpoint, raw_body)

    try:
        result = run_maximize_profit_optimization(_build_request_data(payload, raw_body))
        _log_response(result)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result)

        return result
    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        error_data = _error_payload(e)
        _log_response(error_data)
        raise HTTPException(status_code=500, detail=error_data)


@router.post("/maximize-profit-percent", response_model=PriceGenixResponse)
async def maximize_profit_percent(request: Request, payload: PriceGenixRequest):
    """
    **MAXIMIZE PORTFOLIO MARGIN %**

    Optimizes prices across all 6 brands to maximize portfolio profit margin percentage.

    **Objective:** max(Total Profit / Total GMV × 100)
    """
    endpoint = "/maximize-profit-percent"
    raw_body = await request.json()
    _log_request(endpoint, raw_body)

    try:
        result = run_maximize_profit_percent_optimization(_build_request_data(payload, raw_body))
        _log_response(result)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result)

        return result
    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        error_data = _error_payload(e)
        _log_response(error_data)
        raise HTTPException(status_code=500, detail=error_data)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "PriceGenix Optimization API",
        "version": "1.0.0"
    }

"""
MarketEdge API Endpoints
3 endpoints: maximize-roas, maximize-gmv, minimize-spend
"""

from fastapi import APIRouter, HTTPException, Request
from app.models.market_edge_models import OptimizationRequest, OptimizationResponse, ErrorResponse
from app.services.market_edge.maximize_roas import run_maximize_roas_optimization
from app.services.market_edge.maximize_gmv import run_maximize_gmv_optimization
from app.services.market_edge.minimize_spend import run_minimize_spend_optimization
import json
import os
import datetime
import uuid
import traceback

# Create APIRouter
router = APIRouter(
    prefix="/api/v1/market-edge",
    tags=["MarketEdge Optimization"]
)

from typing import Any, Optional

LOG_FILE = "debug_market_edge.log"

def log_debug(step: str, data: Any, request_id: Optional[str] = None):
    """
    Helper to print structured debug logs to file and console
    Now supports Request ID for tracing specific API calls
    """
    try:
        timestamp = datetime.datetime.now().isoformat()
        req_id_str = f"[{request_id}] " if request_id else ""
        
        # Header
        log_entry = f"\n[MarketEdge DEBUG] {timestamp} {req_id_str}- {step}:\n"
        log_entry += "-" * 60 + "\n"
        
        # Data Body
        if isinstance(data, (dict, list)):
            log_entry += json.dumps(data, indent=2, default=str)
        else:
            log_entry += str(data)
            
        log_entry += "\n" + "="*60 + "\n"
        
        # Print to console for immediate visibility
        print(log_entry)
        
        # Write to file for persistence
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
    except Exception as e:
        print(f"FAILED TO LOG: {e}")

@router.post("/maximize-roas", response_model=OptimizationResponse)
async def maximize_roas(request: OptimizationRequest):
    """
    MAXIMIZE PORTFOLIO ROAS
    """
    request_id = str(uuid.uuid4())[:8]
    try:
        req_data = request.dict()
        req_data["request_id"] = request_id  # Inject ID for downstream logging
        
        log_debug("INCOMING REQUEST (Maximize ROAS)", req_data, request_id)
        
        # Validate critical inputs
        if request.test_spread_min is None or request.test_spread_max is None:
             log_debug("WARNING: Missing Test Spreads", "test_spread_min or test_spread_max is NONE", request_id)

        # ✅ LOG FUNDS AND CONSTRAINTS FOR VERIFICATION
        log_debug("Funds Received", {
            "seo_funds": request.seo_funds,
            "smm_funds": request.smm_funds,
            "ooh_funds": request.ooh_funds
        }, request_id)

        log_debug("Channel Constraints Received", {
            "seo_roas_min": request.seo_roas_min,
            "smm_roas_min": request.smm_roas_min,
            "ooh_roas_min": request.ooh_roas_min,
            "seo_mroas_min": request.seo_mroas_min,
            "smm_mroas_min": request.smm_mroas_min,
            "ooh_mroas_min": request.ooh_mroas_min
        }, request_id)

        result = run_maximize_roas_optimization(req_data)
        
        log_debug("OUTGOING RESPONSE (Maximize ROAS)", result, request_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result)
        
        return result
    
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        error_msg = f"INTERNAL SERVER ERROR: {str(e)}"
        log_debug("CRASH/ERROR", f"{error_msg}\n{traceback.format_exc()}", request_id)
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})


@router.post("/maximize-gmv", response_model=OptimizationResponse)
async def maximize_gmv(request: OptimizationRequest):
    """
    MAXIMIZE TOTAL GMV
    """
    request_id = str(uuid.uuid4())[:8]
    try:
        req_data = request.dict()
        req_data["request_id"] = request_id
        
        log_debug("INCOMING REQUEST (Maximize GMV)", req_data, request_id)
        
        # ✅ LOG FUNDS AND CONSTRAINTS FOR VERIFICATION
        log_debug("Funds Received", {
            "seo_funds": request.seo_funds,
            "smm_funds": request.smm_funds,
            "ooh_funds": request.ooh_funds
        }, request_id)

        log_debug("Channel Constraints Received", {
            "seo_roas_min": request.seo_roas_min,
            "smm_roas_min": request.smm_roas_min,
            "ooh_roas_min": request.ooh_roas_min,
            "seo_mroas_min": request.seo_mroas_min,
            "smm_mroas_min": request.smm_mroas_min,
            "ooh_mroas_min": request.ooh_mroas_min
        }, request_id)

        # Start optimization
        result = run_maximize_gmv_optimization(req_data)
        
        log_debug("OUTGOING RESPONSE (Maximize GMV)", result, request_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result)
        
        return result
    
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = f"INTERNAL SERVER ERROR: {str(e)}"
        log_debug("CRASH/ERROR", f"{error_msg}\n{traceback.format_exc()}", request_id)
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})


@router.post("/minimize-spend", response_model=OptimizationResponse)
async def minimize_spend(request: OptimizationRequest):
    """
    MINIMIZE TOTAL SPEND
    """
    request_id = str(uuid.uuid4())[:8]
    try:
        req_data = request.dict()
        req_data["request_id"] = request_id
        
        log_debug("INCOMING REQUEST (Minimize Spend)", req_data, request_id)
        
        # ✅ LOG FUNDS AND CONSTRAINTS FOR VERIFICATION
        log_debug("Funds Received", {
            "seo_funds": request.seo_funds,
            "smm_funds": request.smm_funds,
            "ooh_funds": request.ooh_funds
        }, request_id)

        log_debug("Channel Constraints Received", {
            "seo_roas_min": request.seo_roas_min,
            "smm_roas_min": request.smm_roas_min,
            "ooh_roas_min": request.ooh_roas_min,
            "seo_mroas_min": request.seo_mroas_min,
            "smm_mroas_min": request.smm_mroas_min,
            "ooh_mroas_min": request.ooh_mroas_min
        }, request_id)

        result = run_minimize_spend_optimization(req_data)
        
        log_debug("OUTGOING RESPONSE (Minimize Spend)", result, request_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result)
        
        return result
    
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = f"INTERNAL SERVER ERROR: {str(e)}"
        log_debug("CRASH/ERROR", f"{error_msg}\n{traceback.format_exc()}", request_id)
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})

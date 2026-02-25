"""
CORE OPTIMIZATION ENGINE
⚠️ ALL FORMULAS ARE PRESERVED FROM ORIGINAL CODE
This contains the exact calculation logic - no modifications
"""

import numpy as np
from typing import Dict, Any
from app.core.constants import CHANNELS, SPEND_STEP




import json
import os
import datetime
from typing import Optional

LOG_FILE = "debug_market_edge.log"

def log_debug(step: str, data: Any, request_id: Optional[str] = None):
    """Helper to print structured debug logs to file and console"""
    try:
        timestamp = datetime.datetime.now().isoformat()
        req_id_str = f"[{request_id}] " if request_id else ""
        
        log_entry = f"\n[MarketEdge OPTIMIZER] {timestamp} {req_id_str}- {step}:\n"
        try:
            if isinstance(data, (dict, list)):
                log_entry += json.dumps(data, indent=2, default=str)
            else:
                log_entry += str(data)
        except:
            log_entry += str(data)
        log_entry += "\n" + "-"*60 + "\n"
        
        print(log_entry)
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
    except Exception as e:
        print(f"Failed to write log: {e}")

def apply_test_spread(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate test_min/test_max for ALL channels based on test_spread values and available funds.
    """
    # Extract request_id if present
    request_id = request_data.get("request_id")
    
    channels_copy = {}
    
    test_spread_min = request_data.get("test_spread_min")
    test_spread_max = request_data.get("test_spread_max")
    
    # Map channel keys to funds keys
    funds_map = {
        "Search Engine Optimisation": request_data.get("seo_funds"),
        "Social Media Marketing": request_data.get("smm_funds"),
        "Out of Home (Billboards)": request_data.get("ooh_funds")
    }
    
    # Log raw funds input
    log_debug("Raw Funds Input", funds_map, request_id)

    for channel_name, channel_data in CHANNELS.items():
        channels_copy[channel_name] = channel_data.copy()
        
        # Determine Base Value
        funds = funds_map.get(channel_name)
        
        if test_spread_min is None:
            channels_copy[channel_name]["test_min"] = int(channel_data["model_min"])
        else:
            channels_copy[channel_name]["test_min"] = int(channel_data["model_min"] * (1 - test_spread_min))
            
        # --- MAX CALCULATION ---
        # Base max matches model max always
        base_max = channel_data["model_max"]
             
        if test_spread_max is None:
            # If no spread, usage model_max, but clip to funds if available
            val = int(base_max)
            if funds is not None:
                val = min(val, funds)
            channels_copy[channel_name]["test_max"] = val
        else:
            # If spread, calculate from model_max, then clip to funds
            val = int(base_max * (1 + test_spread_max))
            if funds is not None:
                val = min(val, funds)
            channels_copy[channel_name]["test_max"] = val
    
    # Format log data
    log_data = {
        "spread_min": test_spread_min,
        "spread_max": test_spread_max,
        "funds_provided": funds_map,
        "result_ranges": {
            ch: {
                "base_range": [data['model_min'], data['model_max']], 
                "calculated_test_range": [data.get('test_min'), data.get('test_max')]
            } for ch, data in channels_copy.items()
        }
    }
    log_debug("Applied Test Spread Result", log_data, request_id)
    
    return channels_copy


def calculate_gmv_roas(x1: float, x2: float, x3: float, 
                       channels: Dict, roas_spread_percent: float) -> Dict[str, float]:
    """
    ⚠️ EXACT CALCULATION FROM ORIGINAL CODE - NO CHANGES
    
    Calculate GMV, ROAS, PED and all related metrics
    
    FORMULAS (PRESERVED):
    1. GMV = m * Spend + c
    2. ROAS = GMV / Spend
    3. ROAS Spread Upper = Spend × (1 + roas_spread_percent)
    4. ROAS Spread Lower = Spend × (1 - roas_spread_percent)
    5. GMV Spread = m * ROAS_Spread + c
    6. Delta ROAS = ROAS_Upper - ROAS_Lower
    7. Delta GMV = GMV_Upper - GMV_Lower
    8. mROAS = Delta GMV / Delta ROAS (should equal 'm')
    9. PED = mROAS * Spend / GMV
    """
    
    A = channels["Search Engine Optimisation"]
    B = channels["Social Media Marketing"]
    C = channels["Out of Home (Billboards)"]
    
    # ========== STEP 1: Calculate GMV for each channel ==========
    # FORMULA: GMV = m * Spend + c
    gmv1 = A["m"] * x1 + A["c"]
    gmv2 = B["m"] * x2 + B["c"]
    gmv3 = C["m"] * x3 + C["c"]
    
    # No negative GMV
    gmv1 = max(0, gmv1)
    gmv2 = max(0, gmv2)
    gmv3 = max(0, gmv3)
    
    # Round GMV
    gmv1 = round(gmv1)
    gmv2 = round(gmv2)
    gmv3 = round(gmv3)
    
    # ========== STEP 2: Calculate ROAS ==========
    # FORMULA: ROAS = GMV / Spend
    roas1 = gmv1 / x1 if x1 > 0 else 0
    roas2 = gmv2 / x2 if x2 > 0 else 0
    roas3 = gmv3 / x3 if x3 > 0 else 0
    
    # ========== STEP 3: Total metrics ==========
    total_gmv = gmv1 + gmv2 + gmv3
    total_spend = x1 + x2 + x3
    portfolio_roas = total_gmv / total_spend if total_spend > 0 else 0
    
    # ========== STEP 4: ROAS Spread calculations ==========
    # FORMULA: ROAS Spread = Spend × (1 ± roas_spread_percent)
    roas_spread_u1 = x1 * (1 + roas_spread_percent)
    roas_spread_l1 = x1 * (1 - roas_spread_percent)
    roas_spread_u2 = x2 * (1 + roas_spread_percent)
    roas_spread_l2 = x2 * (1 - roas_spread_percent)
    roas_spread_u3 = x3 * (1 + roas_spread_percent)
    roas_spread_l3 = x3 * (1 - roas_spread_percent)
    
    # ========== STEP 5: GMV Spread calculations ==========
    # FORMULA: GMV = m * Spend + c (applied to spread values)
    gmv_spread_u1 = A["m"] * roas_spread_u1 + A["c"]
    gmv_spread_l1 = A["m"] * roas_spread_l1 + A["c"]
    gmv_spread_u2 = B["m"] * roas_spread_u2 + B["c"]
    gmv_spread_l2 = B["m"] * roas_spread_l2 + B["c"]
    gmv_spread_u3 = C["m"] * roas_spread_u3 + C["c"]
    gmv_spread_l3 = C["m"] * roas_spread_l3 + C["c"]
    
    # ========== STEP 6: Delta calculations ==========
    delta_roas1 = roas_spread_u1 - roas_spread_l1
    delta_gmv1 = gmv_spread_u1 - gmv_spread_l1
    delta_roas2 = roas_spread_u2 - roas_spread_l2
    delta_gmv2 = gmv_spread_u2 - gmv_spread_l2
    delta_roas3 = roas_spread_u3 - roas_spread_l3
    delta_gmv3 = gmv_spread_u3 - gmv_spread_l3
    
    # ========== STEP 7: mROAS verification ==========
    # FORMULA: mROAS = Delta GMV / Delta ROAS (should equal 'm')
    mroas_calc1 = delta_gmv1 / delta_roas1 if delta_roas1 > 0 else 0
    mroas_calc2 = delta_gmv2 / delta_roas2 if delta_roas2 > 0 else 0
    mroas_calc3 = delta_gmv3 / delta_roas3 if delta_roas3 > 0 else 0
    
    # ========== STEP 8: PED (Price Elasticity of Demand) ==========
    # FORMULA: PED = mROAS * Spend / GMV
    ped1 = mroas_calc1 * x1 / gmv1 if gmv1 > 0 else 0
    ped2 = mroas_calc2 * x2 / gmv2 if gmv2 > 0 else 0
    ped3 = mroas_calc3 * x3 / gmv3 if gmv3 > 0 else 0
    
    # Return all calculated values (EXACT format from original)
    return {
        "gmv1": gmv1, "gmv2": gmv2, "gmv3": gmv3,
        "roas1": roas1, "roas2": roas2, "roas3": roas3,
        "mroas1": mroas_calc1, "mroas2": mroas_calc2, "mroas3": mroas_calc3,
        "ped1": ped1, "ped2": ped2, "ped3": ped3,
        "roas_spread_u1": roas_spread_u1, "roas_spread_l1": roas_spread_l1,
        "roas_spread_u2": roas_spread_u2, "roas_spread_l2": roas_spread_l2,
        "roas_spread_u3": roas_spread_u3, "roas_spread_l3": roas_spread_l3,
        "gmv_spread_u1": gmv_spread_u1, "gmv_spread_l1": gmv_spread_l1,
        "gmv_spread_u2": gmv_spread_u2, "gmv_spread_l2": gmv_spread_l2,
        "gmv_spread_u3": gmv_spread_u3, "gmv_spread_l3": gmv_spread_l3,
        "delta_roas1": delta_roas1, "delta_gmv1": delta_gmv1,
        "delta_roas2": delta_roas2, "delta_gmv2": delta_gmv2,
        "delta_roas3": delta_roas3, "delta_gmv3": delta_gmv3,
        "total_gmv": total_gmv,
        "total_spend": total_spend,
        "portfolio_roas": portfolio_roas,
    }


def calculate_spend_rank_scale(result: Dict[str, float]) -> Dict[str, float]:
    """
    ⚠️ EXACT FORMULA FROM ORIGINAL CODE
    
    Calculate Spend Rank and Spend Scale based on PED values
    
    LOGIC (PRESERVED):
    1. Rank channels by PED (descending) - highest PED = rank 1
    2. Calculate x = 100 / (Min_PED - Max_PED)
    3. Calculate y = PED - Min_PED
    4. Spend Scale = abs(y * x)
    """
    
    # Get PED values with channel IDs
    peds = [
        (1, result["ped1"]),
        (2, result["ped2"]),
        (3, result["ped3"])
    ]
    
    # Sort by PED (descending) - highest PED gets rank 1
    peds_sorted = sorted(peds, key=lambda x: x[1], reverse=True)
    
    # Assign ranks
    ranks = {}
    for rank, (channel_id, ped_value) in enumerate(peds_sorted, 1):
        ranks[channel_id] = rank
    
    # Get min and max PED
    ped_values = [result["ped1"], result["ped2"], result["ped3"]]
    min_ped = min(ped_values)
    max_ped = max(ped_values)
    
    # FORMULA: x = 100 / (Min_PED - Max_PED)
    x = 100 / (min_ped - max_ped) if (min_ped - max_ped) != 0 else 0
    
    # Calculate y and spend_scale for each channel
    y1 = result["ped1"] - min_ped
    y2 = result["ped2"] - min_ped
    y3 = result["ped3"] - min_ped
    
    spend_scale1 = abs(y1 * x)
    spend_scale2 = abs(y2 * x)
    spend_scale3 = abs(y3 * x)
    
    return {
        "rank1": ranks[1],
        "rank2": ranks[2],
        "rank3": ranks[3],
        "spend_scale1": spend_scale1,
        "spend_scale2": spend_scale2,
        "spend_scale3": spend_scale3,
    }


def check_constraints(result: Dict[str, float], constraints: Dict[str, Any]) -> bool:
    """
    ⚠️ EXACT CONSTRAINT CHECKING FROM ORIGINAL CODE
    
    Check if results satisfy all global and channel-level constraints
    Returns True if all constraints are satisfied, False otherwise
    """
    # print(f"DEBUG: Checking constraints: {json.dumps(constraints, default=str)}")
    
    # ========== GLOBAL CONSTRAINTS ==========
    
    # GMV constraints
    if constraints.get("gmv_lower") is not None:
        if result["total_gmv"] < constraints["gmv_lower"]:
            return False
    
    if constraints.get("gmv_upper") is not None:
        if result["total_gmv"] > constraints["gmv_upper"]:
            return False
    
    # Spend constraints
    if constraints.get("spend_lower") is not None:
        if result["total_spend"] < constraints["spend_lower"]:
            return False
    
    if constraints.get("spend_upper") is not None:
        if result["total_spend"] > constraints["spend_upper"]:
            return False
    
    # Portfolio ROAS constraints
    if constraints.get("roas_lower") is not None:
        if result["portfolio_roas"] < constraints["roas_lower"]:
            return False
    
    if constraints.get("roas_upper") is not None:
        if result["portfolio_roas"] > constraints["roas_upper"]:
            return False
    
    # ========== CHANNEL-LEVEL CONSTRAINTS ==========
    
    # SEO (Channel 1) constraints
    if constraints.get("seo_roas_min") is not None:
        if result["roas1"] < constraints["seo_roas_min"]:
            return False
    if constraints.get("seo_roas_max") is not None:
        if result["roas1"] > constraints["seo_roas_max"]:
            # print(f"DEBUG: SEO ROAS Max failed: {result['roas1']} > {constraints['seo_roas_max']}")
            return False
    if constraints.get("seo_mroas_min") is not None:
        if result["mroas1"] < constraints["seo_mroas_min"]:
            return False
    if constraints.get("seo_mroas_max") is not None:
        if result["mroas1"] > constraints["seo_mroas_max"]:
            return False
    
    # SMM (Channel 2) constraints
    if constraints.get("smm_roas_min") is not None:
        if result["roas2"] < constraints["smm_roas_min"]:
            return False
    if constraints.get("smm_roas_max") is not None:
        if result["roas2"] > constraints["smm_roas_max"]:
            return False
    if constraints.get("smm_mroas_min") is not None:
        if result["mroas2"] < constraints["smm_mroas_min"]:
            return False
    if constraints.get("smm_mroas_max") is not None:
        if result["mroas2"] > constraints["smm_mroas_max"]:
            return False
    
    # OOH (Channel 3) constraints
    if constraints.get("ooh_roas_min") is not None:
        if result["roas3"] < constraints["ooh_roas_min"]:
            return False
    if constraints.get("ooh_roas_max") is not None:
        if result["roas3"] > constraints["ooh_roas_max"]:
            return False
    if constraints.get("ooh_mroas_min") is not None:
        if result["mroas3"] < constraints["ooh_mroas_min"]:
            return False
    if constraints.get("ooh_mroas_max") is not None:
        if result["mroas3"] > constraints["ooh_mroas_max"]:
            return False
    
    return True

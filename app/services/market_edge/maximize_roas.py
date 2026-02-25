"""
MAXIMIZE ROAS OPTIMIZATION
⚠️ EXACT LOGIC FROM maximize_roas_marketing.py
"""

import numpy as np
import time
from typing import Dict, Any
from app.services.market_edge.optimizer import (
    apply_test_spread, calculate_gmv_roas, 
    calculate_spend_rank_scale, check_constraints
)
from app.core.constants import SPEND_STEP, ROAS_SPREAD_PERCENT  # ✅ Import hardcoded value


def run_maximize_roas_optimization(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    MAXIMIZE PORTFOLIO ROAS
    ⚠️ EXACT ALGORITHM FROM ORIGINAL FILE
    
    Uses HARDCODED roas_spread_percent from constants (0.001)
    """
    
    start_time = time.time()
    
    # Apply test spread to get test_min and test_max
    channels = apply_test_spread(request_data)
    
    A = channels["Search Engine Optimisation"]
    B = channels["Social Media Marketing"]
    C = channels["Out of Home (Billboards)"]
    
    # Create spend ranges
    x1_vals = np.arange(A["test_min"], A["test_max"] + 1, SPEND_STEP)
    x2_vals = np.arange(B["test_min"], B["test_max"] + 1, SPEND_STEP)
    x3_vals = np.arange(C["test_min"], C["test_max"] + 1, SPEND_STEP)
    
    total_iterations = len(x1_vals) * len(x2_vals) * len(x3_vals)
    
    # Initialize best solution
    best = {"roas": -1e18}
    
    total = 0
    passed = 0
    
    # MAIN OPTIMIZATION LOOP
    for x1 in x1_vals:
        for x2 in x2_vals:
            for x3 in x3_vals:
                total += 1
                
                # Calculate all metrics using HARDCODED roas_spread_percent
                result = calculate_gmv_roas(
                    x1, x2, x3, channels, 
                    ROAS_SPREAD_PERCENT  # ✅ Use hardcoded value from constants
                )
                
                result["x1"] = x1
                result["x2"] = x2
                result["x3"] = x3
                
                # Check if constraints are satisfied
                if not check_constraints(result, request_data):
                    continue
                
                passed += 1
                
                # OPTIMIZATION CRITERIA: Maximize portfolio ROAS
                if result["portfolio_roas"] > best["roas"]:
                    best = {
                        "roas": result["portfolio_roas"],
                        "x1": x1,
                        "x2": x2,
                        "x3": x3,
                        "result": result
                    }
    
    end_time = time.time()
    
    # Check if solution found
    if "result" not in best:
        return {
            "status": "error",
            "message": "No solution found. Constraints are too strict.",
            "details": f"Tested {total:,} combinations, none satisfied constraints."
        }
    
    # Calculate spend rank and scale
    r = best["result"]
    rank_scale = calculate_spend_rank_scale(r)
    
    # Format response
    return {
        "status": "success",
        "message": "Optimal solution found - Portfolio ROAS maximized",
        "objective": "maximize_roas",
        "total_spend": r["total_spend"],
        "total_gmv": r["total_gmv"],
        "portfolio_roas": r["portfolio_roas"],
        "seo": {
            "spend": best["x1"],
            "gmv": r["gmv1"],
            "roas": r["roas1"],
            "mroas": r["mroas1"],
            "ped": r["ped1"],
            "rank": rank_scale["rank1"],
            "spend_scale": rank_scale["spend_scale1"],
            "roas_spread_upper": r["roas_spread_u1"],
            "roas_spread_lower": r["roas_spread_l1"],
            "gmv_spread_upper": r["gmv_spread_u1"],
            "gmv_spread_lower": r["gmv_spread_l1"],
            "delta_roas": r["delta_roas1"],
            "delta_gmv": r["delta_gmv1"],
            "test_range_min": A["test_min"],
            "test_range_max": A["test_max"]
        },
        "smm": {
            "spend": best["x2"],
            "gmv": r["gmv2"],
            "roas": r["roas2"],
            "mroas": r["mroas2"],
            "ped": r["ped2"],
            "rank": rank_scale["rank2"],
            "spend_scale": rank_scale["spend_scale2"],
            "roas_spread_upper": r["roas_spread_u2"],
            "roas_spread_lower": r["roas_spread_l2"],
            "gmv_spread_upper": r["gmv_spread_u2"],
            "gmv_spread_lower": r["gmv_spread_l2"],
            "delta_roas": r["delta_roas2"],
            "delta_gmv": r["delta_gmv2"],
            "test_range_min": B["test_min"],
            "test_range_max": B["test_max"]
        },
        "ooh": {
            "spend": best["x3"],
            "gmv": r["gmv3"],
            "roas": r["roas3"],
            "mroas": r["mroas3"],
            "ped": r["ped3"],
            "rank": rank_scale["rank3"],
            "spend_scale": rank_scale["spend_scale3"],
            "roas_spread_upper": r["roas_spread_u3"],
            "roas_spread_lower": r["roas_spread_l3"],
            "gmv_spread_upper": r["gmv_spread_u3"],
            "gmv_spread_lower": r["gmv_spread_l3"],
            "delta_roas": r["delta_roas3"],
            "delta_gmv": r["delta_gmv3"],
            "test_range_min": C["test_min"],
            "test_range_max": C["test_max"]
        },
        "optimization_time": round(end_time - start_time, 2),
        "total_iterations": total,
        "valid_solutions": passed,
        "pass_rate": round(100 * passed / total, 2) if total > 0 else 0
    }

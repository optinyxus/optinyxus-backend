"""
PRICEGENIX - MAXIMIZE PROFIT PERCENTAGE (Margin)
⚠️ EXACT LOGIC FROM maximize_profit_percent.py
"""

import numpy as np
import time
from typing import Dict, Any
from app.services.pricegenix.optimizer import (
    compute_metrics, resolve_stock_bounds, 
    resolve_global_unit_bounds, check_constraints, resolve_brand_stocks
)
from app.core.pricegenix_constants import BRANDS, PRICE_STEP, BRAND_KEYS


def run_maximize_profit_percent_optimization(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    MAXIMIZE PORTFOLIO MARGIN %
    Objective: max(total_profit / total_gmv)
    """
    
    start_time = time.time()
    
    # Get brand configs
    A, B, C, D, E, F = [BRANDS[key] for key in BRAND_KEYS]
    
    # Resolve stock from request payload (fallbacks to defaults if not provided)
    brand_stocks = resolve_brand_stocks(request_data)

    # Resolve stock bounds
    stock_bounds = resolve_stock_bounds(request_data, brand_stocks)
    
    # Resolve global unit bounds
    u_min, u_max = resolve_global_unit_bounds(request_data, brand_stocks)
    
    # Create price ranges for all 6 brands
    x1_vals = np.arange(A["MnP"], A["MxP"] + 1, PRICE_STEP)
    x2_vals = np.arange(B["MnP"], B["MxP"] + 1, PRICE_STEP)
    x3_vals = np.arange(C["MnP"], C["MxP"] + 1, PRICE_STEP)
    x4_vals = np.arange(D["MnP"], D["MxP"] + 1, PRICE_STEP)
    x5_vals = np.arange(E["MnP"], E["MxP"] + 1, PRICE_STEP)
    x6_vals = np.arange(F["MnP"], F["MxP"] + 1, PRICE_STEP)
    
    best = {"val": -1e18}
    total = 0
    passed = 0
    
    # MAIN OPTIMIZATION LOOP
    for x1 in x1_vals:
        for x2 in x2_vals:
            for x3 in x3_vals:
                for x4 in x4_vals:
                    for x5 in x5_vals:
                        for x6 in x6_vals:
                            total += 1
                            
                            # Compute all metrics
                            m = compute_metrics((x1, x2, x3, x4, x5, x6), brand_stocks)
                            
                            # Check constraints
                            if not check_constraints(m, request_data, stock_bounds, u_min, u_max):
                                continue
                            
                            passed += 1
                            
                            # Objective: maximize portfolio margin percentage
                            gmv = m["g1"] + m["g2"] + m["g3"] + m["g4"] + m["g5"] + m["g6"]
                            profit = m["p1"] + m["p2"] + m["p3"] + m["p4"] + m["p5"] + m["p6"]
                            pct_portfolio = profit / gmv if gmv > 0 else 0
                            
                            if pct_portfolio > best["val"]:
                                best = {
                                    "val": pct_portfolio,
                                    "x1": x1, "x2": x2, "x3": x3,
                                    "x4": x4, "x5": x5, "x6": x6,
                                    "metrics": m
                                }
    
    end_time = time.time()
    
    # Check if solution found
    if "metrics" not in best:
        return {
            "status": "error",
            "message": "No solution found. Constraints are too strict.",
            "details": f"Tested {total:,} combinations, none satisfied constraints."
        }
    
    m = best["metrics"]
    
    # Calculate portfolio metrics
    total_gmv = m["g1"] + m["g2"] + m["g3"] + m["g4"] + m["g5"] + m["g6"]
    total_profit = m["p1"] + m["p2"] + m["p3"] + m["p4"] + m["p5"] + m["p6"]
    portfolio_margin = (total_profit / total_gmv * 100) if total_gmv > 0 else 0
    total_units = int(m["n1"] + m["n2"] + m["n3"] + m["n4"] + m["n5"] + m["n6"])
    
    # Format response
    return {
        "status": "success",
        "message": "Optimal solution found - Portfolio Margin % maximized",
        "objective": "maximize_profit_percent",
        "total_gmv": total_gmv,
        "total_profit": total_profit,
        "portfolio_margin_percent": portfolio_margin,
        "total_units": total_units,
        "portfolio_discount_percent": m["d_pct"] * 100,
        
        "bosch": {
            "price": best["x1"],
            "units": int(m["n1"]),
            "gmv": m["g1"],
            "profit": m["p1"],
            "margin_percent": m["p1_pct"] * 100,
            "discount_percent": m["d1_pct_brand"] * 100
        },
        "haier": {
            "price": best["x2"],
            "units": int(m["n2"]),
            "gmv": m["g2"],
            "profit": m["p2"],
            "margin_percent": m["p2_pct"] * 100,
            "discount_percent": m["d2_pct_brand"] * 100
        },
        "ifb": {
            "price": best["x3"],
            "units": int(m["n3"]),
            "gmv": m["g3"],
            "profit": m["p3"],
            "margin_percent": m["p3_pct"] * 100,
            "discount_percent": m["d3_pct_brand"] * 100
        },
        "lg": {
            "price": best["x4"],
            "units": int(m["n4"]),
            "gmv": m["g4"],
            "profit": m["p4"],
            "margin_percent": m["p4_pct"] * 100,
            "discount_percent": m["d4_pct_brand"] * 100
        },
        "samsung": {
            "price": best["x5"],
            "units": int(m["n5"]),
            "gmv": m["g5"],
            "profit": m["p5"],
            "margin_percent": m["p5_pct"] * 100,
            "discount_percent": m["d5_pct_brand"] * 100
        },
        "whirlpool": {
            "price": best["x6"],
            "units": int(m["n6"]),
            "gmv": m["g6"],
            "profit": m["p6"],
            "margin_percent": m["p6_pct"] * 100,
            "discount_percent": m["d6_pct_brand"] * 100
        },
        
        "optimization_time": round(end_time - start_time, 2),
        "total_iterations": total,
        "valid_solutions": passed,
        "pass_rate": round(100 * passed / total, 2) if total > 0 else 0
    }

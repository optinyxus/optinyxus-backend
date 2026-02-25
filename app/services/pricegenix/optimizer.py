"""
PRICEGENIX - CORE OPTIMIZER FUNCTIONS
⚠️ EXACT LOGIC FROM ORIGINAL FILES
"""

import math
from typing import Dict, Any, Tuple
from app.core.pricegenix_constants import BRANDS, PRICE_STEP, ROUND_UNITS, BRAND_KEYS


def compute_metrics(prices: Tuple[float, float, float, float, float, float]) -> Dict[str, Any]:
    """
    Compute all metrics for given prices
    
    Args:
        prices: (x1, x2, x3, x4, x5, x6) = Prices for Bosch, Haier, IFB, LG, Samsung, Whirlpool
    
    Returns:
        Dictionary with all computed metrics
    """
    x1, x2, x3, x4, x5, x6 = prices
    
    # Get brand configs
    A, B, C, D, E, F = [BRANDS[key] for key in BRAND_KEYS]
    
    # Predicted units using linear demand model: units = m * price + c
    n1 = A["m"] * x1 + A["c"]
    n2 = B["m"] * x2 + B["c"]
    n3 = C["m"] * x3 + C["c"]
    n4 = D["m"] * x4 + D["c"]
    n5 = E["m"] * x5 + E["c"]
    n6 = F["m"] * x6 + F["c"]
    
    # No negative units
    n1 = max(0, n1)
    n2 = max(0, n2)
    n3 = max(0, n3)
    n4 = max(0, n4)
    n5 = max(0, n5)
    n6 = max(0, n6)
    
    # Rounding to integer units
    if ROUND_UNITS:
        n1 = math.floor(n1)
        n2 = math.floor(n2)
        n3 = math.floor(n3)
        n4 = math.floor(n4)
        n5 = math.floor(n5)
        n6 = math.floor(n6)
    
    # HARD STOCK CAP
    n1 = min(n1, A["stock"])
    n2 = min(n2, B["stock"])
    n3 = min(n3, C["stock"])
    n4 = min(n4, D["stock"])
    n5 = min(n5, E["stock"])
    n6 = min(n6, F["stock"])
    
    # GMV (revenue)
    g1 = n1 * x1
    g2 = n2 * x2
    g3 = n3 * x3
    g4 = n4 * x4
    g5 = n5 * x5
    g6 = n6 * x6
    
    # Profit (per brand)
    p1 = n1 * (x1 - A["NLC"])
    p2 = n2 * (x2 - B["NLC"])
    p3 = n3 * (x3 - C["NLC"])
    p4 = n4 * (x4 - D["NLC"])
    p5 = n5 * (x5 - E["NLC"])
    p6 = n6 * (x6 - F["NLC"])
    
    # Margin % (per brand)
    p1_pct = p1 / g1 if g1 > 0 else 0
    p2_pct = p2 / g2 if g2 > 0 else 0
    p3_pct = p3 / g3 if g3 > 0 else 0
    p4_pct = p4 / g4 if g4 > 0 else 0
    p5_pct = p5 / g5 if g5 > 0 else 0
    p6_pct = p6 / g6 if g6 > 0 else 0
    
    # Brand-level discount % (price-based)
    d1_pct_brand = (A["MOP"] - x1) / A["MOP"] if A["MOP"] > 0 and x1 <= A["MOP"] else 0
    d2_pct_brand = (B["MOP"] - x2) / B["MOP"] if B["MOP"] > 0 and x2 <= B["MOP"] else 0
    d3_pct_brand = (C["MOP"] - x3) / C["MOP"] if C["MOP"] > 0 and x3 <= C["MOP"] else 0
    d4_pct_brand = (D["MOP"] - x4) / D["MOP"] if D["MOP"] > 0 and x4 <= D["MOP"] else 0
    d5_pct_brand = (E["MOP"] - x5) / E["MOP"] if E["MOP"] > 0 and x5 <= E["MOP"] else 0
    d6_pct_brand = (F["MOP"] - x6) / F["MOP"] if F["MOP"] > 0 and x6 <= F["MOP"] else 0
    
    # Discount amounts in ₹
    d1_amt = max(0, A["MOP"] - x1) * n1
    d2_amt = max(0, B["MOP"] - x2) * n2
    d3_amt = max(0, C["MOP"] - x3) * n3
    d4_amt = max(0, D["MOP"] - x4) * n4
    d5_amt = max(0, E["MOP"] - x5) * n5
    d6_amt = max(0, F["MOP"] - x6) * n6
    d_total = d1_amt + d2_amt + d3_amt + d4_amt + d5_amt + d6_amt
    
    # Portfolio discount %
    mop_gmv1 = n1 * A["MOP"]
    mop_gmv2 = n2 * B["MOP"]
    mop_gmv3 = n3 * C["MOP"]
    mop_gmv4 = n4 * D["MOP"]
    mop_gmv5 = n5 * E["MOP"]
    mop_gmv6 = n6 * F["MOP"]
    total_mop_gmv = mop_gmv1 + mop_gmv2 + mop_gmv3 + mop_gmv4 + mop_gmv5 + mop_gmv6
    
    d_pct = d_total / total_mop_gmv if total_mop_gmv > 0 else 0
    
    return {
        "n1": n1, "n2": n2, "n3": n3, "n4": n4, "n5": n5, "n6": n6,
        "g1": g1, "g2": g2, "g3": g3, "g4": g4, "g5": g5, "g6": g6,
        "p1": p1, "p2": p2, "p3": p3, "p4": p4, "p5": p5, "p6": p6,
        "p1_pct": p1_pct, "p2_pct": p2_pct, "p3_pct": p3_pct,
        "p4_pct": p4_pct, "p5_pct": p5_pct, "p6_pct": p6_pct,
        "d_pct": d_pct,
        "d_total": d_total,
        "d1_pct_brand": d1_pct_brand,
        "d2_pct_brand": d2_pct_brand,
        "d3_pct_brand": d3_pct_brand,
        "d4_pct_brand": d4_pct_brand,
        "d5_pct_brand": d5_pct_brand,
        "d6_pct_brand": d6_pct_brand,
    }


def resolve_stock_bounds(request: Dict[str, Any]) -> Tuple:
    """
    Convert flexible stock bounds (percent/absolute) into concrete unit bounds
    
    Returns:
        Tuple of (bosch_min, bosch_max, haier_min, haier_max, ...)
    """
    bounds = []
    brand_keys = ["bosch", "haier", "ifb", "lg", "samsung", "whirlpool"]
    
    for i, brand_key in enumerate(brand_keys):
        stock = BRANDS[BRAND_KEYS[i]]["stock"]
        
        # Min bound
        n_min_config = request.get(f"{brand_key}_n_min", {"type": "percent", "value": 0.0})
        if n_min_config["type"] == "percent":
            n_min = (n_min_config["value"] or 0.0) * stock
        else:
            n_min = n_min_config["value"] or 0.0
        
        # Max bound
        n_max_config = request.get(f"{brand_key}_n_max", {"type": "percent", "value": 1.0})
        if n_max_config["type"] == "percent":
            n_max = (n_max_config["value"] or 1.0) * stock
        else:
            n_max = n_max_config["value"] or stock
        
        # Clamp to [0, stock]
        n_min = max(0, min(n_min, stock))
        n_max = max(0, min(n_max, stock))
        
        bounds.extend([n_min, n_max])
    
    return tuple(bounds)


def resolve_global_unit_bounds(request: Dict[str, Any]) -> Tuple[float, float]:
    """Resolve global unit bounds (percent or absolute)"""
    total_stock = sum(BRANDS[key]["stock"] for key in BRAND_KEYS)
    
    # Min units
    u_min_config = request.get("units_min")
    if u_min_config is None or u_min_config.get("value") is None:
        u_min = None
    elif u_min_config["type"] == "percent":
        u_min = u_min_config["value"] * total_stock
    else:
        u_min = u_min_config["value"]
    
    # Max units
    u_max_config = request.get("units_max")
    if u_max_config is None or u_max_config.get("value") is None:
        u_max = None
    elif u_max_config["type"] == "percent":
        u_max = u_max_config["value"] * total_stock
    else:
        u_max = u_max_config["value"]
    
    # Clamp
    if u_min is not None:
        u_min = max(0, min(u_min, total_stock))
    if u_max is not None:
        u_max = max(0, min(u_max, total_stock))
    
    return u_min, u_max


def resolve_portfolio_discount_bounds(metrics: Dict[str, Any], request: Dict[str, Any]) -> Tuple:
    """Resolve portfolio discount bounds (percent or absolute)"""
    
    # Calculate total MOP GMV
    total_mop_gmv = sum(
        metrics[f"n{i+1}"] * BRANDS[BRAND_KEYS[i]]["MOP"]
        for i in range(6)
    )
    
    # Min discount
    d_min_config = request.get("discount_min")
    if d_min_config is None or d_min_config.get("value") is None:
        d_min = None
    elif d_min_config["type"] == "percent":
        d_min = d_min_config["value"] * total_mop_gmv if total_mop_gmv > 0 else None
    else:
        d_min = d_min_config["value"]
    
    # Max discount
    d_max_config = request.get("discount_max")
    if d_max_config is None or d_max_config.get("value") is None:
        d_max = None
    elif d_max_config["type"] == "percent":
        d_max = d_max_config["value"] * total_mop_gmv if total_mop_gmv > 0 else None
    else:
        d_max = d_max_config["value"]
    
    return d_min, d_max, metrics["d_total"]


def check_constraints(metrics: Dict[str, Any], request: Dict[str, Any], stock_bounds: Tuple, u_min: float, u_max: float) -> bool:
    """Check all constraints - ⚠️ EXACT LOGIC FROM ORIGINAL"""
    
    # Unpack stock bounds
    bosch_min, bosch_max, haier_min, haier_max, ifb_min, ifb_max, \
    lg_min, lg_max, samsung_min, samsung_max, whirlpool_min, whirlpool_max = stock_bounds
    
    # STOCK UTILIZATION (per brand)
    if not (bosch_min <= metrics["n1"] <= bosch_max):
        return False
    if not (haier_min <= metrics["n2"] <= haier_max):
        return False
    if not (ifb_min <= metrics["n3"] <= ifb_max):
        return False
    if not (lg_min <= metrics["n4"] <= lg_max):
        return False
    if not (samsung_min <= metrics["n5"] <= samsung_max):
        return False
    if not (whirlpool_min <= metrics["n6"] <= whirlpool_max):
        return False
    
    # Portfolio metrics
    g = metrics["g1"] + metrics["g2"] + metrics["g3"] + metrics["g4"] + metrics["g5"] + metrics["g6"]
    p = metrics["p1"] + metrics["p2"] + metrics["p3"] + metrics["p4"] + metrics["p5"] + metrics["p6"]
    u = metrics["n1"] + metrics["n2"] + metrics["n3"] + metrics["n4"] + metrics["n5"] + metrics["n6"]
    pct = p / g if g > 0 else 0
    
    # GMV constraints
    gL = request.get("gmv_lower")
    gU = request.get("gmv_upper")
    if gL is not None and g < gL:
        return False
    if gU is not None and g > gU:
        return False
    
    # Profit constraints
    pL = request.get("profit_lower")
    pU = request.get("profit_upper")
    if pL is not None and p < pL:
        return False
    if pU is not None and p > pU:
        return False
    
    # Portfolio margin constraints
    p_pct_L = request.get("margin_percent_lower")
    p_pct_U = request.get("margin_percent_upper")
    if p_pct_L is not None and pct < p_pct_L:
        return False
    if p_pct_U is not None and pct > p_pct_U:
        return False
    
    # GLOBAL UNIT CONSTRAINTS
    if u_min is not None and u < u_min:
        return False
    if u_max is not None and u > u_max:
        return False
    
    # PORTFOLIO DISCOUNT CONSTRAINTS
    d_min, d_max, d_total = resolve_portfolio_discount_bounds(metrics, request)
    if d_min is not None and d_total < d_min:
        return False
    if d_max is not None and d_total > d_max:
        return False
    
    # BRAND-LEVEL DISCOUNT % CONSTRAINTS
    brand_names = ["bosch", "haier", "ifb", "lg", "samsung", "whirlpool"]
    for i, brand in enumerate(brand_names, 1):
        d_min_key = f"{brand}_discount_pct_min"
        d_max_key = f"{brand}_discount_pct_max"
        
        if d_min_key in request and request[d_min_key] is not None:
            if metrics[f"d{i}_pct_brand"] < request[d_min_key]:
                return False
        if d_max_key in request and request[d_max_key] is not None:
            if metrics[f"d{i}_pct_brand"] > request[d_max_key]:
                return False
    
    return True

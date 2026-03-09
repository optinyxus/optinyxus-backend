"""
PRICEGENIX - CORE OPTIMIZER FUNCTIONS
⚠️ EXACT LOGIC FROM ORIGINAL FILES
"""

import math
from typing import Dict, Any, Tuple, Optional
from app.core.pricegenix_constants import BRANDS, PRICE_STEP, ROUND_UNITS, BRAND_KEYS


def _default_brand_stocks() -> Dict[str, float]:
    """No hardcoded stock fallback; uncapped unless payload provides stock."""
    return {brand_key: float("inf") for brand_key in BRAND_KEYS}


def _coerce_non_negative_number(value: Any) -> Optional[float]:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(parsed) or parsed < 0:
        return None
    return parsed


def _resolve_row_brand_key(row: Dict[str, Any]) -> Optional[str]:
    candidates = [
        row.get("brand"),
        row.get("article"),
        row.get("article_no"),
        row.get("articleNo")
    ]

    for candidate in candidates:
        normalized = str(candidate or "").strip().lower()
        if not normalized:
            continue
        for brand_key in BRAND_KEYS:
            if brand_key.lower() in normalized:
                return brand_key
    return None


def resolve_brand_stocks(request: Dict[str, Any]) -> Dict[str, float]:
    """
    Resolve dynamic per-brand stock from request payload table_data.
    Falls back to configured constants when payload does not provide stock.
    """
    stock_by_brand = _default_brand_stocks()
    table_data = request.get("table_data")
    if not isinstance(table_data, list):
        return stock_by_brand

    aggregated = {brand_key: 0.0 for brand_key in BRAND_KEYS}
    has_payload_stock = {brand_key: False for brand_key in BRAND_KEYS}

    for row in table_data:
        if not isinstance(row, dict):
            continue
        brand_key = _resolve_row_brand_key(row)
        if not brand_key:
            continue

        stock = _coerce_non_negative_number(row.get("stock"))
        if stock is None:
            continue

        aggregated[brand_key] += stock
        has_payload_stock[brand_key] = True

    for brand_key in BRAND_KEYS:
        if has_payload_stock[brand_key]:
            stock_by_brand[brand_key] = aggregated[brand_key]

    return stock_by_brand


def compute_metrics(
    prices: Tuple[float, float, float, float, float, float],
    brand_stocks: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Compute all metrics for given prices
    
    Args:
        prices: (x1, x2, x3, x4, x5, x6) = Prices for Bosch, Haier, IFB, LG, Samsung, Whirlpool
    
    Returns:
        Dictionary with all computed metrics
    """
    x1, x2, x3, x4, x5, x6 = prices
    stock_by_brand = brand_stocks or _default_brand_stocks()
    
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
    n1 = min(n1, stock_by_brand[BRAND_KEYS[0]])
    n2 = min(n2, stock_by_brand[BRAND_KEYS[1]])
    n3 = min(n3, stock_by_brand[BRAND_KEYS[2]])
    n4 = min(n4, stock_by_brand[BRAND_KEYS[3]])
    n5 = min(n5, stock_by_brand[BRAND_KEYS[4]])
    n6 = min(n6, stock_by_brand[BRAND_KEYS[5]])
    
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


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def calculate_portfolio_metrics(metrics: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate portfolio-level metrics required by the API response.
    """
    brand_count = len(BRAND_KEYS)
    total_sales = sum(metrics.get(f"g{i}", 0.0) for i in range(1, brand_count + 1))
    total_profit = sum(metrics.get(f"p{i}", 0.0) for i in range(1, brand_count + 1))
    total_units = sum(metrics.get(f"n{i}", 0.0) for i in range(1, brand_count + 1))
    total_discount = float(metrics.get("d_total", 0.0))

    portfolio_margin_percent = _safe_div(total_profit, total_sales) * 100.0
    portfolio_discount_percent = _safe_div(total_discount, total_discount + total_sales) * 100.0
    test_price = _safe_div(total_sales, total_units)
    discount_per_unit = _safe_div(total_discount, total_units)
    profit_per_unit = _safe_div(total_profit, total_units)
    mop = test_price + discount_per_unit
    nlc = test_price - profit_per_unit

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_units": total_units,
        "portfolio_margin_percent": portfolio_margin_percent,
        "portfolio_discount_total": total_discount,
        "portfolio_discount_percent": portfolio_discount_percent,
        "portfolio_test_price": test_price,
        "portfolio_mop": mop,
        "portfolio_nlc": nlc,
        "portfolio_discount_per_unit": discount_per_unit,
        "portfolio_profit_per_unit": profit_per_unit,
    }


def calculate_brand_ped_metrics(
    prices: Tuple[float, float, float, float, float, float],
    metrics: Dict[str, Any]
) -> Dict[str, Dict[str, float]]:
    """
    Calculate per-brand PED, PED basis, saleability scale, and saleability rank.
    """
    brand_keys_response = [brand.lower() for brand in BRAND_KEYS]
    ped_values = []
    epsilon = 1e-12

    for i, brand_key in enumerate(BRAND_KEYS):
        units = float(metrics.get(f"n{i + 1}", 0.0))
        price = float(prices[i])
        demand_slope = float(BRANDS[brand_key]["m"])
        ped_value = demand_slope * price / (units if abs(units) > epsilon else epsilon)
        ped_values.append((brand_keys_response[i], ped_value))

    series = [value for _, value in ped_values]
    min_ped = min(series) if series else 0.0
    max_ped = max(series) if series else 0.0
    ped_denominator = min_ped - max_ped
    if abs(ped_denominator) <= epsilon:
        ped_denominator = -epsilon
    ped_basis = 100.0 / ped_denominator

    saleability_scale = {
        key: (ped_value - max_ped) * ped_basis
        for key, ped_value in ped_values
    }
    ranked_keys = sorted(brand_keys_response, key=lambda key: saleability_scale[key], reverse=True)
    ranks = {key: rank for rank, key in enumerate(ranked_keys, start=1)}

    brand_ped = {key: ped_value for key, ped_value in ped_values}
    print("\n===== PRICEGENIX PED DEBUG =====")
    print(f"PED Series: {series}")
    print(f"Min PED: {min_ped}")
    print(f"Max PED: {max_ped}")
    print(f"PED_Basis: {ped_basis}")
    print(f"BrandPED: {brand_ped}")
    print(f"SaleabilityScale: {saleability_scale}")

    return {
        key: {
            "ped_basis": ped_basis,
            "saleability_scale": saleability_scale[key],
            "saleability_rank": ranks[key],
        }
        for key in brand_keys_response
    }


def resolve_stock_bounds(request: Dict[str, Any], brand_stocks: Dict[str, float] = None) -> Tuple:
    """
    Convert flexible stock bounds (percent/absolute) into concrete unit bounds
    
    Returns:
        Tuple of (bosch_min, bosch_max, haier_min, haier_max, ...)
    """
    bounds = []
    brand_keys = ["bosch", "haier", "ifb", "lg", "samsung", "whirlpool"]
    stock_by_brand = brand_stocks or _default_brand_stocks()
    
    for i, brand_key in enumerate(brand_keys):
        stock = stock_by_brand[BRAND_KEYS[i]]
        
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


def resolve_global_unit_bounds(
    request: Dict[str, Any],
    brand_stocks: Dict[str, float] = None
) -> Tuple[float, float]:
    """Resolve global unit bounds (percent or absolute)"""
    stock_by_brand = brand_stocks or _default_brand_stocks()
    total_stock = sum(stock_by_brand[key] for key in BRAND_KEYS)
    
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

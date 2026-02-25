"""
Pydantic Models for PriceGenix Request/Response Validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal


# ==================== FLEXIBLE CONSTRAINT MODELS ====================

class FlexibleConstraint(BaseModel):
    """Flexible constraint that supports both percent and absolute values"""
    type: Literal["percent", "absolute"]
    value: Optional[float] = None


# ==================== REQUEST MODEL ====================

class PriceGenixRequest(BaseModel):
    """
    PRICEGENIX REQUEST FROM UI
    
    All parameters sent from frontend on every request.
    Backend hardcoded: brands, price_step=500, round_units=True
    """
    
    # ========== STOCK UTILIZATION (per brand - FLEXIBLE) ==========
    bosch_n_min: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=0.0),
        description="Bosch minimum units: percent (0.0-1.0) or absolute count"
    )
    bosch_n_max: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=1.0),
        description="Bosch maximum units: percent (0.0-1.0) or absolute count"
    )
    
    haier_n_min: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=0.0)
    )
    haier_n_max: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=1.0)
    )
    
    ifb_n_min: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=0.0)
    )
    ifb_n_max: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=1.0)
    )
    
    lg_n_min: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=0.0)
    )
    lg_n_max: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=1.0)
    )
    
    samsung_n_min: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=0.0)
    )
    samsung_n_max: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=1.0)
    )
    
    whirlpool_n_min: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=0.0)
    )
    whirlpool_n_max: FlexibleConstraint = Field(
        default=FlexibleConstraint(type="percent", value=1.0)
    )
    
    # ========== GLOBAL/PORTFOLIO CONSTRAINTS ==========
    gmv_lower: Optional[float] = Field(None, ge=0, description="Minimum total GMV (₹)")
    gmv_upper: Optional[float] = Field(None, ge=0, description="Maximum total GMV (₹)")
    
    profit_lower: Optional[float] = Field(None, ge=0, description="Minimum total profit (₹)")
    profit_upper: Optional[float] = Field(None, ge=0, description="Maximum total profit (₹)")
    
    margin_percent_lower: Optional[float] = Field(None, ge=0, le=1, description="Min portfolio margin %")
    margin_percent_upper: Optional[float] = Field(None, ge=0, le=1, description="Max portfolio margin %")
    
    # ========== GLOBAL UNIT CONSTRAINTS (FLEXIBLE) ==========
    units_min: Optional[FlexibleConstraint] = Field(
        None,
        description="Min total units: percent (0.0-1.0) or absolute count"
    )
    units_max: Optional[FlexibleConstraint] = Field(
        None,
        description="Max total units: percent (0.0-1.0) or absolute count"
    )
    
    # ========== PORTFOLIO DISCOUNT CONSTRAINT (FLEXIBLE) ==========
    discount_min: Optional[FlexibleConstraint] = Field(
        None,
        description="Min portfolio discount: percent (0.0-1.0) or absolute ₹"
    )
    discount_max: Optional[FlexibleConstraint] = Field(
        None,
        description="Max portfolio discount: percent (0.0-1.0) or absolute ₹"
    )
    
    # ========== BRAND-LEVEL DISCOUNT % CONSTRAINTS ==========
    bosch_discount_pct_min: Optional[float] = Field(None, ge=0, le=1)
    bosch_discount_pct_max: Optional[float] = Field(None, ge=0, le=1)
    
    haier_discount_pct_min: Optional[float] = Field(None, ge=0, le=1)
    haier_discount_pct_max: Optional[float] = Field(None, ge=0, le=1)
    
    ifb_discount_pct_min: Optional[float] = Field(None, ge=0, le=1)
    ifb_discount_pct_max: Optional[float] = Field(None, ge=0, le=1)
    
    lg_discount_pct_min: Optional[float] = Field(None, ge=0, le=1)
    lg_discount_pct_max: Optional[float] = Field(None, ge=0, le=1)
    
    samsung_discount_pct_min: Optional[float] = Field(None, ge=0, le=1)
    samsung_discount_pct_max: Optional[float] = Field(None, ge=0, le=1)
    
    whirlpool_discount_pct_min: Optional[float] = Field(None, ge=0, le=1)
    whirlpool_discount_pct_max: Optional[float] = Field(None, ge=0, le=1)

    @validator('gmv_upper')
    def validate_gmv_range(cls, v, values):
        if v is not None and values.get('gmv_lower') is not None:
            if v <= values['gmv_lower']:
                raise ValueError('gmv_upper must be greater than gmv_lower')
        return v
    
    @validator('profit_upper')
    def validate_profit_range(cls, v, values):
        if v is not None and values.get('profit_lower') is not None:
            if v <= values['profit_lower']:
                raise ValueError('profit_upper must be greater than profit_lower')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "bosch_n_min": {"type": "percent", "value": 0.0},
                "bosch_n_max": {"type": "percent", "value": 1.0},
                "haier_n_min": {"type": "percent", "value": 0.0},
                "haier_n_max": {"type": "percent", "value": 1.0},
                "ifb_n_min": {"type": "percent", "value": 0.0},
                "ifb_n_max": {"type": "percent", "value": 1.0},
                "lg_n_min": {"type": "percent", "value": 0.0},
                "lg_n_max": {"type": "percent", "value": 1.0},
                "samsung_n_min": {"type": "percent", "value": 0.0},
                "samsung_n_max": {"type": "percent", "value": 1.0},
                "whirlpool_n_min": {"type": "percent", "value": 0.0},
                "whirlpool_n_max": {"type": "percent", "value": 1.0},
                "gmv_lower": None,
                "gmv_upper": None,
                "profit_lower": None,
                "profit_upper": None,
                "margin_percent_lower": None,
                "margin_percent_upper": None,
                "units_min": None,
                "units_max": None,
                "discount_min": None,
                "discount_max": None,
                "bosch_discount_pct_min": None,
                "bosch_discount_pct_max": None,
                "haier_discount_pct_min": None,
                "haier_discount_pct_max": None,
                "ifb_discount_pct_min": None,
                "ifb_discount_pct_max": None,
                "lg_discount_pct_min": None,
                "lg_discount_pct_max": None,
                "samsung_discount_pct_min": None,
                "samsung_discount_pct_max": None,
                "whirlpool_discount_pct_min": None,
                "whirlpool_discount_pct_max": None,
            }
        }


# ==================== RESPONSE MODELS ====================

class BrandResult(BaseModel):
    """Individual brand optimization results"""
    price: float
    units: int
    gmv: float
    profit: float
    margin_percent: float
    discount_percent: float


class PriceGenixResponse(BaseModel):
    """Complete PriceGenix optimization response"""
    status: str
    message: str
    objective: str  # "maximize_gmv", "maximize_profit", or "maximize_profit_percent"
    
    # Portfolio metrics
    total_gmv: float
    total_profit: float
    portfolio_margin_percent: float
    total_units: int
    portfolio_discount_percent: float
    
    # Individual brand results
    bosch: BrandResult
    haier: BrandResult
    ifb: BrandResult
    lg: BrandResult
    samsung: BrandResult
    whirlpool: BrandResult
    
    # Metadata
    optimization_time: float
    total_iterations: int
    valid_solutions: int
    pass_rate: float


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str
    message: str
    details: Optional[str] = None

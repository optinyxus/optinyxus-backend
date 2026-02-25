"""
Pydantic Models for Request/Response Validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional

# ==================== REQUEST MODELS ====================

class OptimizationRequest(BaseModel):
    """
    REQUEST FROM UI - ALL PARAMETERS
    
    ⚠️ NOTE: roas_spread_percent is HARDCODED in backend (0.001)
           and is NOT part of this request
    """
    
    # ========== TEST SPREAD CONFIGURATION ==========
    # These control the search range for optimization
    # Range: 0 to 0.25 (0% to 25%) or None for no adjustment
    test_spread_min: Optional[float] = Field(
        None, 
        ge=0, 
        le=0.25, 
        description="Test spread min: 0 to 0.25 or null"
    )
    test_spread_max: Optional[float] = Field(
        None, 
        ge=0, 
        le=0.25, 
        description="Test spread max: 0 to 0.25 or null"
    )
    
    # ========== GLOBAL/PORTFOLIO CONSTRAINTS ==========
    gmv_lower: Optional[float] = Field(None, ge=0, description="Minimum total GMV (₹)")
    gmv_upper: Optional[float] = Field(None, ge=0, description="Maximum total GMV (₹)")
    spend_lower: Optional[float] = Field(None, ge=0, description="Minimum total spend (₹)")
    spend_upper: Optional[float] = Field(None, ge=0, description="Maximum total spend (₹)")
    roas_lower: Optional[float] = Field(None, ge=0, description="Minimum portfolio ROAS")
    roas_upper: Optional[float] = Field(None, ge=0, description="Maximum portfolio ROAS")
    
    # ========== SEO CHANNEL CONSTRAINTS ==========
    seo_roas_min: Optional[float] = Field(None, ge=0, description="Min ROAS for SEO channel")
    seo_roas_max: Optional[float] = Field(None, ge=0, description="Max ROAS for SEO channel")
    seo_mroas_min: Optional[float] = Field(None, ge=0, description="Min mROAS for SEO channel")
    seo_mroas_max: Optional[float] = Field(None, ge=0, description="Max mROAS for SEO channel")
    
    # ========== SMM CHANNEL CONSTRAINTS ==========
    smm_roas_min: Optional[float] = Field(None, ge=0, description="Min ROAS for SMM channel")
    smm_roas_max: Optional[float] = Field(None, ge=0, description="Max ROAS for SMM channel")
    smm_mroas_min: Optional[float] = Field(None, ge=0, description="Min mROAS for SMM channel")
    smm_mroas_max: Optional[float] = Field(None, ge=0, description="Max mROAS for SMM channel")
    
    # ========== OOH CHANNEL CONSTRAINTS ==========
    ooh_roas_min: Optional[float] = Field(None, ge=0, description="Min ROAS for OOH channel")
    ooh_roas_max: Optional[float] = Field(None, ge=0, description="Max ROAS for OOH channel")
    ooh_mroas_min: Optional[float] = Field(None, ge=0, description="Min mROAS for OOH channel")
    ooh_mroas_max: Optional[float] = Field(None, ge=0, description="Max mROAS for OOH channel")

    # ========== CHANNEL FUNDS (FROM CSV) ==========
    seo_funds: Optional[float] = Field(None, ge=0, description="Funds available for SEO")
    smm_funds: Optional[float] = Field(None, ge=0, description="Funds available for SMM")
    ooh_funds: Optional[float] = Field(None, ge=0, description="Funds available for OOH")

    @validator('test_spread_min', 'test_spread_max')
    def validate_test_spread(cls, v):
        """Validate test spread is between 0 and 0.25 if provided"""
        if v is not None and not (0 <= v <= 0.25):
            raise ValueError('Test spread must be between 0 and 0.25 (0% to 25%)')
        return v
    
    @validator('gmv_upper')
    def validate_gmv_range(cls, v, values):
        """Ensure GMV upper > GMV lower if both provided"""
        if v is not None and values.get('gmv_lower') is not None:
            if v <= values['gmv_lower']:
                raise ValueError('gmv_upper must be greater than gmv_lower')
        return v
    
    @validator('spend_upper')
    def validate_spend_range(cls, v, values):
        """Ensure Spend upper > Spend lower if both provided"""
        if v is not None and values.get('spend_lower') is not None:
            if v <= values['spend_lower']:
                raise ValueError('spend_upper must be greater than spend_lower')
        return v
    
    @validator('roas_upper')
    def validate_roas_range(cls, v, values):
        """Ensure ROAS upper > ROAS lower if both provided"""
        if v is not None and values.get('roas_lower') is not None:
            if v <= values['roas_lower']:
                raise ValueError('roas_upper must be greater than roas_lower')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "test_spread_min": 0.20,
                "test_spread_max": 0.20,
                "gmv_lower": None,
                "gmv_upper": None,
                "spend_lower": None,
                "spend_upper": None,
                "roas_lower": None,
                "roas_upper": None,
                "seo_roas_min": None,
                "seo_roas_max": None,
                "seo_mroas_min": None,
                "seo_mroas_max": None,
                "smm_roas_min": None,
                "smm_roas_max": None,
                "smm_mroas_min": None,
                "smm_mroas_max": None,
                "ooh_roas_min": None,
                "ooh_roas_max": None,
                "ooh_mroas_min": None,
                "ooh_mroas_max": None
            }
        }


# ==================== RESPONSE MODELS ====================

class ChannelResult(BaseModel):
    """Individual channel optimization results"""
    spend: float
    gmv: float
    roas: float
    mroas: float
    ped: float
    rank: int
    spend_scale: float
    
    # Spread values
    roas_spread_upper: float
    roas_spread_lower: float
    gmv_spread_upper: float
    gmv_spread_lower: float
    delta_roas: float
    delta_gmv: float

    # Test Range Values (Exposed from Backend)
    test_range_min: Optional[float] = None
    test_range_max: Optional[float] = None


class OptimizationResponse(BaseModel):
    """Complete optimization response"""
    status: str
    message: str
    objective: str
    
    # Portfolio metrics
    total_spend: float
    total_gmv: float
    portfolio_roas: float
    
    # Individual channel results
    seo: ChannelResult
    smm: ChannelResult
    ooh: ChannelResult
    
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

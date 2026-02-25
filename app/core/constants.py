"""
HARDCODED CHANNEL CONFIGURATIONS
⚠️ DO NOT MODIFY - Backend Constants
"""

# Fixed spend step - DO NOT CHANGE
SPEND_STEP = 50000

# ⚠️ HARDCODED ROAS SPREAD PERCENTAGE - DO NOT CHANGE
# This is used for calculating marginal ROAS and PED
# 0.001 = 0.1%
ROAS_SPREAD_PERCENT = 0.001

# Channel configurations with LINEAR MODEL: GMV = m * Spend + c
CHANNELS = {
    "Search Engine Optimisation": {
        "m": 9.07261591,                    # Slope (mROAS)
        "c": -63917.4052628055,             # Intercept
        "model_min": 309683,                 # ✅ Backend hardcoded
        "model_max": 6181381,                # ✅ Backend hardcoded
    },
    "Social Media Marketing": {
        "m": 8.8538013359,
        "c": -107974.063447397,
        "model_min": 232262,
        "model_max": 4636036,
    },
    "Out of Home (Billboards)": {
        "m": 8.0290577689,
        "c": 532754.612254743,
        "model_min": 154841,
        "model_max": 3090691,
    },
}

# Channel name mapping for easier access
CHANNEL_NAMES = {
    "seo": "Search Engine Optimisation",
    "smm": "Social Media Marketing",
    "ooh": "Out of Home (Billboards)"
}

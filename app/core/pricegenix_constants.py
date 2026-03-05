"""
PRICEGENIX - HARDCODED CONFIGURATIONS
⚠️ DO NOT MODIFY - Backend Constants Only
"""

# ✅ HARDCODED: Price step for optimization
PRICE_STEP = 500

# ✅ HARDCODED: Always round units to integers
ROUND_UNITS = True

# ✅ HARDCODED: 6 Brand configurations with demand models
BRANDS = {
    "Bosch": {
        "m": -0.0972790276444851,      # Slope (demand sensitivity)
        "c": 3510.26182452518,          # Intercept
        "MnP": 30441.2696987403,        # Minimum price
        "MxP": 36980.8705006165,        # Maximum price
        "NLC": 30441.2696987403,        # Net Landed Cost
        "MOP": 36980.8705006165,        # Maximum Operating Price
    },
    "Haier": {
        "m": -0.0283857208688361,
        "c": 593.827888866882,
        "MnP": 16653.5568327957,
        "MxP": 19073.7003225806,
        "NLC": 16653.5568327957,
        "MOP": 19073.7003225806,
    },
    "IFB": {
        "m": -0.117591805717103,
        "c": 3958.67838055113,
        "MnP": 29976.2293260321,
        "MxP": 34036.011123318,
        "NLC": 29976.2293260321,
        "MOP": 34036.011123318,
    },
    "LG": {
        "m": -0.202215461595577,
        "c": 6714.61166894299,
        "MnP": 27063.8675748679,
        "MxP": 32424.1593257662,
        "NLC": 27063.8675748679,
        "MOP": 32424.1593257662,
    },
    "Samsung": {
        "m": -0.270154262961802,
        "c": 7283.8524094582,
        "MnP": 22131.0209166431,
        "MxP": 25250.3253045419,
        "NLC": 22131.0209166431,
        "MOP": 25250.3253045419,
    },
    "Whirlpool": {
        "m": -0.0255824392916389,
        "c": 1050.67308786139,
        "MnP": 16375.0638217344,
        "MxP": 19966.914912843,
        "NLC": 16375.0638217344,
        "MOP": 19966.914912843,
    },
}

# Brand name shortcuts
BRAND_KEYS = ["Bosch", "Haier", "IFB", "LG", "Samsung", "Whirlpool"]

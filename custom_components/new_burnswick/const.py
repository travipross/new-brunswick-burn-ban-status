"""Constants for the New Brunswick Burn Ban Status integration."""

DOMAIN = "new_burnswick"

CONF_COUNTY = "county"

# The GNB GIS server generates new records around 11 AM Atlantic
UPDATE_HOUR_DATA = 11
UPDATE_MINUTE = 5

# List of all New Brunswick counties as returned by the GIS API (capitalized)
COUNTIES = [
    "ALBERT",
    "CARLETON",
    "CHARLOTTE",
    "GLOUCESTER",
    "KENT",
    "KINGS",
    "MADAWASKA",
    "NORTHUMBERLAND",
    "QUEENS",
    "RESTIGOUCHE",
    "SAINT JOHN",
    "SUNBURY",
    "VICTORIA",
    "WESTMORLAND",
    "YORK",
]

API_URL = "https://gis-erd-der.gnb.ca/gisserver/rest/services/FireWeather/BurnCategories/MapServer/0/query?where=1%3D1&outFields=NAME%2CVALIDDATE%2CPUBLICCATEGORY&returnGeometry=false&f=pjson"
MAP_URL = "https://www3.gnb.ca/public/fire-feu/maps/cat1.png"

# State & Attribute Mappings
STATUS_MAPPING = {
    0: "unknown",
    1: "none",
    2: "limited",
    3: "allowed",
}

ICON_MAPPING = {
    0: "mdi:help-network",
    1: "mdi:fire-off",
    2: "mdi:fire-alert",
    3: "mdi:fire",
}

TEXT_MAPPING = {
    0: "Unknown",
    1: "No burning allowed",
    2: "Burning allowed between 8pm and 8am",
    3: "Burning allowed",
}

COLOR_MAPPING = {
    0: "unknown",
    1: "red",
    2: "yellow",
    3: "green",
}

RGB_MAPPING = {
    0: [128, 128, 128],  # Gray
    1: [255, 0, 0],  # Red
    2: [255, 255, 0],  # Yellow
    3: [0, 255, 0],  # Green
}

# Unique ID suffixes
UID_SUFFIX_CATEGORY = "burn_ban_category"
UID_SUFFIX_BURNING_ALLOWED = "burning_currently_allowed"
UID_SUFFIX_MAP = "burn_ban_map"
UID_SUFFIX_REFRESH = "refresh_burn_ban_data"
UID_SUFFIX_NEXT_UPDATE = "next_burn_ban_data_update"

# Device ID suffixes
DID_SUFFIX_COMMON = "common"

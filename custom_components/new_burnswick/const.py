"""Constants for the New Brunswick Burn Ban Status integration."""

DOMAIN = "new_burnswick"

CONF_COUNTY = "county"

# Default update interval (30 minutes)
UPDATE_INTERVAL_MINUTES = 30

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

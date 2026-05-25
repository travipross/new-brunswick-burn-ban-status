"""Constants for the New Brunswick Burn Ban Status integration."""

DOMAIN = "new_burnswick"

CONF_COUNTY = "county"

# The GNB GIS server generates new records around 11 AM Atlantic
# But the public "effective" time is 2 PM Atlantic.
UPDATE_HOUR_DATA = 11
UPDATE_HOUR_PUBLIC = 14
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
    1: [255, 0, 0],    # Red
    2: [255, 255, 0],  # Yellow
    3: [0, 255, 0],    # Green
}

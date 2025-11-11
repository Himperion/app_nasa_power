import geopandas as gpd
from shapely.geometry import Point
import pycountry

# Cargar dataset mundial
world = gpd.read_file("files/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")

def countryFlagEmoji(iso_code):
    try:
        country = pycountry.countries.get(alpha_3=iso_code)
        if not country:
            return ""
        code2 = country.alpha_2
        return chr(ord(code2[0]) + 127397) + chr(ord(code2[1]) + 127397)
    except Exception:
        return ""

def getCountryAndFlag(lat, lon):
    point = Point(lon, lat)
    match = world[world.contains(point)]
    if not match.empty:
        name = match.iloc[0]["NAME_ES"]
        iso = match.iloc[0]["ISO_A3"]
        flag = countryFlagEmoji(iso)
        return name, flag
    return "Unknown", "❌"


"""Alle indstillinger ét sted. Ingen anden fil indeholder konstanter."""
import os

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
SHELLY_IP = os.getenv("SHELLY_IP", "192.168.0.209")
DRY_RUN   = os.getenv("DRY_RUN", "true").lower() == "true"

DB = dict(
    host     = os.getenv("DB_HOST", "localhost"),
    dbname   = os.getenv("DB_NAME", "affugter"),
    user     = os.getenv("DB_USER", "affugter"),
    password = os.environ["DB_PASS"], 
)


CHEAP_HOURS = 3          # antal billigste timer der maa bruges
# TZ_OFFSET   = 2          # sommertid. Vintertid = 1. Skift 25. okt 2026.

PRICE_URL = "https://billigkwh.dk/api/Priser/HentPriser"
PRICE_PARAMS = {
    "sted": "DK2",
    "netselskab": "radius_c",
    "produkt": "andel_energi_flexenergi",
}
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/json",
}

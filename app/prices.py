"""Hentning af priser fra ekstern kilde og beregning af billige timer."""
import datetime as dt

import requests
from app.database import db, local_now   

from app.config import CHEAP_HOURS, HEADERS, PRICE_PARAMS, PRICE_URL


def fetch_and_store():
    """
    Henter dagens priser og gemmer dem.
    Kan koeres flere gange uden skade (idempotent) via ON CONFLICT.
    """
    r = requests.get(PRICE_URL, params=PRICE_PARAMS,
                     headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()
    days = data if isinstance(data, list) else [data]

    result = []
    for d in days:
        priser = d.get("priser")
        if not priser or len(priser) != 24:
            continue

        # ADVARSEL: 'dato' er maerket med Z (UTC), men indeksene foelger
        # dansk lokaltid. Verificeret ved at billigste timer falder midt
        # paa dagen (sol) og dyreste kl. 19-20 (aftenspids).
        day = dt.date.fromisoformat(d["dato"][:10])
        threshold = sorted(priser)[CHEAP_HOURS - 1]

        with db() as conn, conn.cursor() as cur:
            for hour, price in enumerate(priser):
                cur.execute(
                    "INSERT INTO prices (day, hour, price, is_cheap) "
                    "VALUES (%s, %s, %s, %s) "
                    "ON CONFLICT (day, hour) DO UPDATE "
                    "SET price = EXCLUDED.price, is_cheap = EXCLUDED.is_cheap",
                    (day, hour, price, price <= threshold),
                )

        result.append({"day": str(day), "threshold": round(threshold, 2)})

    return result

def price_is_cheap():
    """
    True  = billig time
    False = dyr time
    None  = prisen er ukendt  -> logic.py behandler den som billig (F5)
    """
    now = local_now()
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT is_cheap FROM prices WHERE day=%s AND hour=%s",
                    (now.date(), now.hour))
        row = cur.fetchone()
    return row[0] if row else None
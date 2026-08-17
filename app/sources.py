"""Vaelger hvilken sensor der maa styre beslutningen."""
import datetime as dt
from app.database import dict_cursor, local_now

MAX_AGE = {"arduino": 180, "zigbee": 1800}   # sekunder
PRIORITY = ["zigbee", "arduino"]


def latest(source):
    with dict_cursor() as cur:
        cur.execute(
            "SELECT * FROM readings WHERE source = %s "
            "ORDER BY ts DESC LIMIT 1", (source,))
        return cur.fetchone()


def current_humidity():
    """Returnerer (humidity, source) eller (None, None) hvis alt er gammelt."""
    now = local_now()
    for src in PRIORITY:
        row = latest(src)
        if not row:
            continue
        ts = row["ts"]
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=now.tzinfo)
        if (now - ts).total_seconds() < MAX_AGE[src]:
            return float(row["humidity"]), src
    return None, None
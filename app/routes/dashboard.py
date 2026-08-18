"""
Endpoints til browseren. Her maa svarene gerne vaere rige paa detaljer -
modtageren har baade hukommelse og en JSON-parser.
"""
import datetime as dt

from fastapi import APIRouter, HTTPException
from app.adapters import shelly
from app.database import db, dict_cursor, local_now
from app.prices import fetch_and_store

router = APIRouter(tags=["dashboard"])


@router.post("/fetch-prices")
def fetch_prices():
    """Henter dagens priser. Kaldes af cron én gang i doegnet."""
    result = fetch_and_store()
    if not result:
        raise HTTPException(502, "Ingen brugbare prisdata fra kilden")
    return {"stored": result}


@router.get("/prices")
def prices(day: str = None):
    """Fuld prisdata til grafer og fejlsoegning."""
    d = dt.date.fromisoformat(day) if day else local_now().date()
    with dict_cursor() as cur:
        cur.execute(
            "SELECT hour, price, is_cheap FROM prices "
            "WHERE day = %s ORDER BY hour", (d,))
        rows = cur.fetchall()

    if not rows:
        raise HTTPException(404, f"Ingen prisdata for {d}")

    cheap = [r["price"] for r in rows if r["is_cheap"]]
    lo = min(r["price"] for r in rows)
    hi = max(r["price"] for r in rows)
    return {
        "day": str(d),
        "threshold": max(cheap) if cheap else None,
        "min": lo,
        "max": hi,
        "ratio": round(hi / lo, 1) if lo > 0 else None,
        "hours": rows,
    }


@router.get("/status")
def status():
    """Seneste maaling plus noegletal."""
    with dict_cursor() as cur:
        cur.execute("SELECT * FROM readings ORDER BY ts DESC LIMIT 1")
        latest = cur.fetchone()
        cur.execute("SELECT count(*) AS n FROM readings")
        total = cur.fetchone()["n"]
        cur.execute("SELECT reason, count(*) AS n FROM switches "
                    "GROUP BY reason ORDER BY n DESC")
        reasons = cur.fetchall()

    stale = None
    if latest:
        age = (dt.datetime.now(dt.timezone.utc) - latest["ts"]).total_seconds()
        if latest["source"] == "zigbee":
            limit = 1800     # 30 min - zigbee-sensoren holder pauser
        else:
            limit = 120      # 2 min - arduino sender hvert 30. sek
        stale = age > limit

    return {
        "latest": latest,
        "stale": stale,          # true = vi har ikke hoert fra Arduinoen
        "total_readings": total,
        "switch_reasons": reasons,
    }


@router.get("/history")
def history(hours: int = 24):
    """Maalinger for de sidste N timer. Til grafer."""
    with dict_cursor() as cur:
        cur.execute(
            "SELECT ts, humidity, temperature, plug_on, price FROM readings "
            "WHERE ts > now() - make_interval(hours => %s) ORDER BY ts",
            (hours,))
        rows = cur.fetchall()
    return {"hours": hours, "count": len(rows), "readings": rows}


@router.get("/plug")
def plug():
    """Live tilstand paa stikket. Spoerger Shelly direkte (ikke databasen)."""
    on, watt = shelly.get_status()
    return {"on": on, "watt": watt, "reachable": on is not None}


@router.get("/switches")
def switches(limit: int = 20):
    """De sidste skift af stikket - 'dagbogen'. Til tabellen i dashboardet."""
    with dict_cursor() as cur:
        cur.execute(
            "SELECT ts, turned_on, reason, humidity, price FROM switches "
            "ORDER BY ts DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
    return {"count": len(rows), "switches": rows}


@router.get("/health")
def health():
    """Simpelt tjek af om serveren og databasen svarer."""
    try:
        with db() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        return {"ok": True}
    except Exception as e:
        raise HTTPException(503, f"Database utilgaengelig: {e}")

"""
Endpoints som mikrocontrolleren kalder.

Svarene holdes bevidst simple: ren tekst hvor det er muligt, saa
Arduinoen hverken skal parse JSON, sortere eller beregne noget.
"""
import datetime as dt

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.database import current_price, db, local_now
from app.models import Reading, SwitchEvent

router = APIRouter(tags=["arduino"])


@router.post("/readings")
def post_reading(r: Reading):
    """Periodisk maaling. Arduinoen sender hvert 30. sekund."""
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO readings (humidity, temperature, plug_on, price) "
            "VALUES (%s, %s, %s, %s)",
            (r.humidity, r.temperature, r.plug_on, current_price()),
        )
    return {"ok": True}


@router.post("/switches")
def post_switch(s: SwitchEvent):
    """
    Haendelse: udgangen skiftede faktisk tilstand.
    Logges KUN efter at Shelly har bekraeftet kommandoen.
    """
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO switches (turned_on, reason, humidity, price) "
            "VALUES (%s, %s, %s, %s)",
            (s.turned_on, s.reason, s.humidity, current_price()),
        )
    return {"ok": True}


@router.get("/cheap", response_class=PlainTextResponse)
def cheap_hours():
    """24 tegn, ét pr. time. '1' = billig."""
    today = local_now().date()
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT hour, is_cheap FROM prices WHERE day = %s ORDER BY hour",
            (today,),
        )
        rows = cur.fetchall()

    if len(rows) != 24:
        raise HTTPException(503, "Ingen prisdata for i dag")

    return "".join("1" if is_cheap else "0" for _, is_cheap in rows)


@router.get("/time", response_class=PlainTextResponse)
def server_time():
    """Epoch-sekunder i UTC. Bruges naar NTP er blokeret paa skolenettet."""
    return str(int(dt.datetime.now(dt.timezone.utc).timestamp()))

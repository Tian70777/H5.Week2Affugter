"""Databaseforbindelse og tidshjaelpere. Ingen forretningslogik her."""
import datetime as dt
from contextlib import contextmanager
from zoneinfo import ZoneInfo  

import psycopg2
import psycopg2.extras

from app.config import DB

DK = ZoneInfo("Europe/Copenhagen")   

@contextmanager
def db():
    """Aabner og lukker forbindelsen automatisk - ogsaa ved fejl."""
    conn = psycopg2.connect(**DB)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def dict_cursor():
    """Cursor der giver dicts i stedet for tupler. Til JSON-svar."""
    with db() as conn:
        with conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur


def local_now():
    """
    Dansk lokaltid. ZoneInfo kender selv sommer- og vintertid,
    saa 25. okt. 2026 haandteres automatisk. (Risiko R11 lukket.)
    """
    return dt.datetime.now(DK)


def current_price():
    """Prisen for den nuvaerende time, eller None hvis ukendt."""
    now = local_now()
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT price FROM prices WHERE day = %s AND hour = %s",
                    (now.date(), now.hour))
        row = cur.fetchone()
    return row[0] if row else None

# ------------------------------------------------------------------
# Historik: skift af stikket. Flyttet hertil fra main.py, fordi
# det er SQL og dermed "hvordan", ikke "hvad".
# ------------------------------------------------------------------

def last_switch_seconds():
    """Sekunder siden stikket sidst skiftede. Stort tal = ingen laas."""
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT ts FROM switches ORDER BY ts DESC LIMIT 1")
        row = cur.fetchone()

    if not row:
        return 10 ** 6                    # aldrig skiftet
    ts = row[0]
    now = local_now()
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=now.tzinfo)
    return int((now - ts).total_seconds())


def log_switch(on, reason, humidity):
    """Logges KUN efter at Shelly har bekraeftet kommandoen."""
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO switches (turned_on, reason, humidity, price) "
            "VALUES (%s,%s,%s,%s)",
            (on, reason, humidity, current_price()),
        )
"""
Styresloejfen. Koerer for evigt, uafhaengigt af webserveren.

Kun ledningsfoering: hent fakta -> spoerg hjernen -> udfoer dommen.
Ingen SQL, ingen HTTP, ingen JSON i denne fil.
"""
import time

from app.adapters import mqtt_source, shelly
from app.database import last_switch_seconds, local_now, log_switch
from app.logic import decide
from app.prices import price_is_cheap
from app.sources import current_humidity

DRY_RUN = True          # TRIN 4: log kun, roer ikke stikket
TICK = 60               # sekunder mellem beslutninger


def tick():
    humidity, src = current_humidity()
    plug_on, watt = shelly.get_status()

    if plug_on is None:                       # Shelly svarer ikke
        print(f"{local_now():%H:%M:%S}  ADVARSEL: Shelly uden svar")
        return

    d = decide(
        humidity=humidity,
        price_is_cheap=price_is_cheap(),
        plug_on=plug_on,
        secs_since_switch=last_switch_seconds(),
        local_hour=local_now().hour,
    )

    h = f"{humidity:.1f}%" if humidity is not None else "?"
    print(f"{local_now():%H:%M:%S}  {h} ({src})  stik={plug_on}  "
          f"{watt}W  -> {d.action}  [{d.reason}]")

    want = {"ON": True, "OFF": False}.get(d.action)
    if want is None or want == plug_on:
        return                                # HOLD, eller allerede korrekt

    if DRY_RUN:
        print(f"           (DRY_RUN: ville skifte til {want})")
        return

    if shelly.set_switch(want):               # log KUN efter bekraeftelse
        log_switch(want, d.reason, humidity)


if __name__ == "__main__":
    mqtt_source.start_background()
    print(f"Styring startet. DRY_RUN={DRY_RUN}")
    while True:
        try:
            tick()
        except Exception as e:
            print(f"FEJL i tick: {e}")        # loeb videre, doe ikke
        time.sleep(TICK)
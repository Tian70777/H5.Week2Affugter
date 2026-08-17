"""
Beslutningslogik. Ren funktion: fakta ind, dom ud.

Denne fil maa IKKE importere database, mqtt, requests eller shelly.
Det er hele pointen: reglerne kan testes uden hardware.
"""
from dataclasses import dataclass

# --- Fugtgraenser (%) ---
H_DANGER = 70.0     # skimmelrisiko: koer uanset pris
H_SAVE   = 60.0     # koer kun hvis strommen er billig
H_OFF    = 45.0     # tort nok: stop

# --- Kompressorbeskyttelse (sekunder) ---
# MIN_OFF = 15 * 60
# MIN_ON  = 10 * 60

MIN_OFF = 60      # TESTING: 1 minute
MIN_ON  = 60      # TESTING: 1 minute

# --- IF4: stilletid ---
QUIET_FROM = 0      # kl. 00
QUIET_TO   = 3      # kl. 03
QUIET_OVERRIDE_ABOVE = 80.0   # noedsituation bryder stilletiden


@dataclass
class Decision:
    action: str     # "ON" | "OFF" | "HOLD"
    reason: str     # menneskelaesbar begrundelse - logges altid


def in_quiet_hours(hour: int) -> bool:
    return QUIET_FROM <= hour < QUIET_TO


def decide(humidity, price_is_cheap, plug_on,
           secs_since_switch, local_hour) -> Decision:
    """
    humidity        float eller None (None = ingen frisk maaling)
    price_is_cheap  True / False / None (None = pris ukendt)
    plug_on         bool - stikkets nuvaerende tilstand
    secs_since_switch  int - sekunder siden sidste skift
    local_hour      int 0-23 - dansk lokaltid
    """

    # IF5: blind = sluk. Vi ved ikke om rummet er vaadt eller tort.
    if humidity is None:
        return Decision("OFF", "IF5: ingen frisk sensordata - sikker tilstand")

    # IF1/IF2: kompressorbeskyttelse. Gaelder FOER alt andet.
    if plug_on and secs_since_switch < MIN_ON:
        return Decision("HOLD", f"IF1: min. {MIN_ON//60} min taendt")
    if not plug_on and secs_since_switch < MIN_OFF:
        return Decision("HOLD", f"IF2: min. {MIN_OFF//60} min slukket")

    # F3: tort nok
    if humidity <= H_OFF:
        return Decision("OFF", f"F3: {humidity:.1f}% <= {H_OFF}% - tort nok")

    # IF4: stilletid blokerer kun START, ikke fortsat drift
    if not plug_on and in_quiet_hours(local_hour):
        if humidity < QUIET_OVERRIDE_ABOVE:
            return Decision("HOLD",
                            f"IF4: stilletid kl. {local_hour:02d} "
                            f"({humidity:.1f}% < {QUIET_OVERRIDE_ABOVE}%)")

    # F1: skimmelrisiko slaar pris
    if humidity >= H_DANGER:
        return Decision("ON", f"F1: {humidity:.1f}% >= {H_DANGER}% "
                              f"- skimmelrisiko, pris ignoreres")

    # F2 + F5: spareomraadet
    if humidity >= H_SAVE:
        if price_is_cheap is True:
            return Decision("ON", f"F2: {humidity:.1f}% og billig strom")
        if price_is_cheap is None:
            return Decision("ON", f"F5: {humidity:.1f}%, pris ukendt "
                                  f"- behandles som billig")
        return Decision("HOLD", f"F2: {humidity:.1f}% men dyr strom - venter")

    return Decision("HOLD", f"{humidity:.1f}% i normalomraadet")
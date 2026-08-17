"""Shelly Gen3 via RPC. Kender intet til fugt eller priser."""
import requests

SHELLY_IP = "192.168.0.209"
TIMEOUT = 5


def set_switch(on: bool) -> bool:
    """Returnerer True hvis Shelly bekraeftede kommandoen."""
    try:
        r = requests.get(f"http://{SHELLY_IP}/rpc/Switch.Set",
                         params={"id": 0, "on": str(on).lower()},
                         timeout=TIMEOUT)
        r.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[shelly] FEJL: {e}")
        return False


def get_status():
    """(is_on, power_watt) eller (None, None) hvis Shelly ikke svarer."""
    try:
        r = requests.get(f"http://{SHELLY_IP}/rpc/Switch.GetStatus",
                         params={"id": 0}, timeout=TIMEOUT)
        r.raise_for_status()
        d = r.json()
        return d.get("output"), d.get("apower")
    except (requests.RequestException, ValueError):
        return None, None
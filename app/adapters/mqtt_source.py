"""Lytter paa Zigbee2MQTT og gemmer maalinger med source='zigbee'."""
import json
import os
import threading

import paho.mqtt.client as mqtt

from app.database import db

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = 1883
TOPIC = "zigbee2mqtt/+"          # + = kun ét niveau, undgaar bridge-stoej
CLIENT_ID = "affugter-listener"


def _on_connect(client, userdata, flags, rc, props):
    print(f"[mqtt] forbundet, abonnerer paa {TOPIC}")
    client.subscribe(TOPIC, qos=1)


def _on_message(client, userdata, msg):
    try:
        d = json.loads(msg.payload.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return
    if not isinstance(d, dict) or "humidity" not in d:
        return

    device = msg.topic.split("/")[-1]
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO readings "
            "(source, device, humidity, temperature, battery, linkquality) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            ("zigbee", device, d.get("humidity"), d.get("temperature"),
             d.get("voltage"), d.get("linkquality")),
        )
    print(f"[mqtt] {device}  {d.get('humidity')}%  {d.get('temperature')}C")


def start_background():
    """Starter lytteren i en baggrundstraad."""
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                    client_id=CLIENT_ID, clean_session=False)
    c.on_connect = _on_connect
    c.on_message = _on_message
    c.reconnect_delay_set(1, 60)
    c.connect_async(MQTT_HOST, MQTT_PORT, keepalive=60)
    threading.Thread(target=c.loop_forever, daemon=True).start()
    return c
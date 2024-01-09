import paho.mqtt.client as mqtt
from random import randrange, uniform
import time
import json

TOPIC = "orinlakantobad"
USERNAME = "Paso"
UID = "45654312"  #  13357647

reader_data = {
    "type": "access",
    "time": 1572542188,
    "isKnown": "true",
    "access": "Admin",
    "username": USERNAME,
    "uid": UID,
    "door": "esp-rfid",
}
payload = json.dumps(reader_data)
# mqtt_broker = 'mqtt.eclipseprojects.io'
mqtt_broker = "broker.hivemq.com"
client = mqtt.Client("Cafeteria")
client.connect(mqtt_broker)

while True:
    client.publish(TOPIC, payload)
    print(f"Just published {payload} to topic {TOPIC}")
    time.sleep(5)

# client.disconnect()

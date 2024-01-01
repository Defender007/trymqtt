import paho.mqtt.client as mqtt
from random import randrange, uniform
import time

TOPIC = 'orinlakantobad'
# mqtt_broker = 'mqtt.eclipseprojects.io'
mqtt_broker = 'broker.hivemq.com'
client = mqtt.Client('Temperature_inside')
client.connect(mqtt_broker)

while True:
    rand_number = uniform(20.0, 21.0)
    # client.publish('TEMPERATURE', rand_number)
    client.publish(TOPIC, rand_number)
    print(f"Just published {str(rand_number)} to topic {TOPIC}")
    time.sleep(1)
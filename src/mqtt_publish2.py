import paho.mqtt.client as mqtt
from random import randrange, uniform
import time

mqtt_broker = 'mqtt.eclipseprojects.io'
client = mqtt.Client('Temperature_Outside')
client.connect(mqtt_broker)

while True:
    rand_number = randrange(10)
    client.publish('TEMPERATURE', rand_number)
    print(f"Just published {str(rand_number)} to topic TEMPERATURE")
    time.sleep(1)
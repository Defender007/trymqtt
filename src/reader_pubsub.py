import os
import django
import paho.mqtt.client as mqtt
from random import randrange, uniform
import time
import uuid
import json

# from django.apps import apps
# from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mealmanager.settings')
django.setup()

from core import models

# transaction = models.Transaction()

TOPIC = 'orinlakantobad'
MY_MESSAGE = "ACCESS GRANTED"
mqtt_broker = 'broker.hivemq.com'
# mqtt_broker = 'mqtt.eclipseprojects.io'
client = mqtt.Client('apiMonitor')
client.connect(mqtt_broker)


def on_message(client, userdata, message):
    rand_number = randrange(10)
    # uni_number = uniform(20.0, 20.1)
    uid = uuid.uuid4()
    transaction = models.Transaction()
    transaction.swipe_count = rand_number
    transaction.reader_uid = str(uid)
    transaction.save()
    client.publish(TOPIC, MY_MESSAGE)
    
    time.sleep(2)

    print(f'Recieved message: {str(message.payload.decode("utf-8"))}')

client.on_message = on_message
client.subscribe(TOPIC)
client.loop_forever()

# while True:
#     transaction = models.Transaction()
#     rand_number = randrange(10)
#     uni_number = uniform(20.0, 20.1)
#     uid = uuid.uuid4()
    
#     client.publish('TEMPERATURE', rand_number)
#     transaction.swipe_count = rand_number
#     transaction.reader_uid = str(uid)
#     transaction.save()
    
#     print(f"Just published {str(rand_number)} to topic TEMPERATURE")
#     time.sleep(1)


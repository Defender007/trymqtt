import os
import time
from datetime import datetime, date
from random import randrange, uniform
import django
import paho.mqtt.client as mqtt
import uuid
import json

# from django.apps import apps
# from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mealmanager.settings')
django.setup()

from django.utils import timezone
from django.db import models
from core.models import Transaction
from users.models import User, UserProfile


# transaction = Transaction()

TOPIC = 'orinlakantobad'
ACCESS_GRANTED = "ACCESS GRANTED"
ACCESS_DENIED = "ACCESS DENIED"
mqtt_broker = 'broker.hivemq.com'
# mqtt_broker = 'mqtt.eclipseprojects.io'
client = mqtt.Client('apiMonitor')
client.connect(mqtt_broker)

def on_message(client, userdata, message):
    reader_message = message.payload.decode("UTF-8");
    print(f'Recieved message: {str(message.payload.decode("utf-8"))}')
    if not reader_message.startswith("ACCESS"):
        parsed_message = json.loads(reader_message)
        reader_uid = parsed_message['uid']
        reader_username = parsed_message['username']
        current_user = User.objects.filter(username=reader_username).first()
        user_profile = None
        if current_user:
            user_profile = UserProfile.objects.filter(user=current_user.pk).first()
            if user_profile is None:
                client.publish(TOPIC, ACCESS_DENIED)
                print("***->RETURNING.... NO USER PROFILE!")
                return
            print("***User Profile***: ", user_profile)
            try: 
                today = timezone.now().date()
                user_transaction = Transaction.objects.get(reader_uid=reader_uid,date__date=today)
                print("THIS IS THE TRANSACTION OBJECT:", user_transaction)
                swipe_count = user_transaction.swipe_count
                meal_category = user_transaction.user.meal_category
                if swipe_count < meal_category:
                    swipe_count += 1
                    user_transaction.swipe_count = swipe_count
                    user_transaction.save()
                    client.publish(TOPIC, ACCESS_GRANTED)
                    print("***->RETURNING.... ENJOY YOUR MEAL!")
                    return
                else:
                    client.publish(TOPIC, ACCESS_DENIED)
                    print("***->RETURNING....YOU HAD ENOUGH MEAL TODAY!")
                    return
            except Exception as e:
                print("Exception: ", e)
                if user_profile:
                    user_transaction = Transaction(swipe_count=1,reader_uid=reader_uid,
                                                 date=timezone.now(), user=user_profile)
                    user_transaction.save()
                    client.publish(TOPIC, ACCESS_GRANTED)
                    print("***->RETURNING....Created TRANSACTION:", user_transaction)
                    return
        else:
            client.publish(TOPIC, ACCESS_DENIED)
            print("User not found!")
    # time.sleep(2)

client.on_message = on_message
client.subscribe(TOPIC)
client.loop_forever()




# while True:
#     transaction = Transaction()
#     rand_number = randrange(10)
#     uni_number = uniform(20.0, 20.1)
#     uid = uuid.uuid4()
    
#     client.publish('TEMPERATURE', rand_number)
#     transaction.swipe_count = rand_number
#     transaction.reader_uid = str(uid)
#     transaction.save()
    
#     print(f"Just published {str(rand_number)} to topic TEMPERATURE")
#     time.sleep(1)


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
ACCESS_DENIED = "ACCESS_DENIED"
mqtt_broker = 'broker.hivemq.com'
# mqtt_broker = 'mqtt.eclipseprojects.io'
client = mqtt.Client('apiMonitor')
client.connect(mqtt_broker)

def on_message(client, userdata, message):
    reader_message = message.payload.decode("UTF-8");
    # if reader_message.startswith("ACCESS_"):
    #     print("***READER",reader_message)
    print(f'Recieved message: {str(message.payload.decode("utf-8"))}')
    if not reader_message.startswith("ACCESS_"):
        parsed_message = json.loads(reader_message)
        print("Door Payload", parsed_message)
        reader_uid = parsed_message['uid']
        reader_username = parsed_message['username']
        print("***Reader Username***: ", reader_username)
        current_user = User.objects.filter(username=reader_username).first()
        print("***Current User***: ", current_user.pk)
        user_profile = None
        if current_user:
            user_profile = UserProfile.objects.filter(user=current_user.pk).first()
            print("***User Profile***: ", user_profile)
            try: 
                today = timezone.now().date()
                # user_transaction = Transaction.objects.filter(reader_uid=reader_uid,date=datetime.now()).first()
                user_transaction = Transaction.objects.get(reader_uid=reader_uid,date__date=today) #date__date=date.today()
                print("THIS IS THE TRANSACTION OBJECT:", user_transaction)
                swipe_count = user_transaction.swipe_count
                meal_category = user_transaction.user.meal_category
                if swipe_count <= meal_category:
                    swipe_count += 1
                    user_transaction.swipe_count = swipe_count
                    user_transaction.save()
                    client.publish(TOPIC, ACCESS_GRANTED)
                else:
                    client.publish(TOPIC, ACCESS_DENIED)
                    print("YOU HAD ENOUGH MEAL TODAY!")
            except Exception as e:
                print("Exception: ", e)
                if user_profile:
                    user_transaction = Transaction(swipe_count=1,reader_uid=reader_uid,
                                                 date=timezone.now(), user=user_profile )
                    user_transaction.save()
                    # client.publish(TOPIC, ACCESS_GRANTED)
                # if user_profile:
                #     user_transaction = Transaction()
                #     user_transaction.swipe_count = 1
                #     user_transaction.reader_uid = reader_uid
                #     user_transaction.date = timezone.now()
                #     user_transaction.user = user_profile
        else:
            client.publish(TOPIC, ACCESS_DENIED)
            print("User not found!")
    # time.sleep(2)
    # print(f'Recieved message: {str(message.payload.decode("utf-8"))}')

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


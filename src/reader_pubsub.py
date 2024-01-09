import os
import time
from datetime import datetime, date
from random import randrange, uniform
import django
from django.core.exceptions import ObjectDoesNotExist
import paho.mqtt.client as mqtt
import uuid
import json


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mealmanager.settings")
django.setup()

from django.utils import timezone
from django.db import models
from core.models import Transaction
from users.models import User, UserProfile


TOPIC = "orinlakantobad"
ACCESS_GRANTED = "ACCESS GRANTED"
ACCESS_DENIED = "ACCESS DENIED"
ACCESS_POINT = 'LOCAL'
mqtt_broker = "broker.hivemq.com"
# mqtt_broker = 'mqtt.eclipseprojects.io'
client = mqtt.Client("apiMonitor")
client.connect(mqtt_broker)


def is_json(data):
    try:
        json.loads(data)
        return True
    except ValueError:
        return False


def on_message(client, userdata, message):
    reader_message = message.payload.decode("UTF-8")
    print(f'Recieved message: {str(message.payload.decode("utf-8"))}')
    if not reader_message.startswith("ACCESS") and is_json(reader_message):
        parsed_message = json.loads(reader_message)
        reader_uid = parsed_message["uid"]
        reader_username = parsed_message["username"]
        owner = User.objects.filter(username=reader_username).first()
        owner_profile = None
        if owner:
            owner_profile = UserProfile.objects.filter(user=owner.pk).first()
            if owner_profile is None:
                client.publish(TOPIC, ACCESS_DENIED)
                print("***->RETURNING.... NO USER PROFILE!")
                return
            print("***User Profile***: ", owner_profile)
            try:
                today = timezone.now().date()
                today_transaction = Transaction.objects.filter(
                    reader_uid=reader_uid, grant_type=ACCESS_GRANTED, date__date=today
                )
                print("THIS IS THE TRANSACTION OBJECT:", today_transaction)

                if today_transaction.first() is None:
                    raise ObjectDoesNotExist("No transaction exists yet for this owner")

                transaction_count = today_transaction.count()
                meal_category = today_transaction.first().owner.meal_category
                SWIPE_COUNT = transaction_count
                if SWIPE_COUNT < meal_category:
                    SWIPE_COUNT += 1
                    today_new_transaction = Transaction(
                        owner=owner_profile,
                        authorizer=owner_profile,
                        swipe_count=SWIPE_COUNT,
                        reader_uid=reader_uid,
                        access_point=ACCESS_POINT,
                        raw_payload=reader_message,
                        grant_type=ACCESS_GRANTED,
                    )
                    today_new_transaction.save()
                    # client.publish(TOPIC, ACCESS_GRANTED)
                    print("***->RETURNING.... ENJOY YOUR MEAL!")
                    return
                    
                else:
                    client.publish(TOPIC, ACCESS_DENIED)
                    print("***->RETURNING....YOU HAD ENOUGH MEAL TODAY!")
                    return
            except ObjectDoesNotExist as e:
                print("Exception: ", e)
                if owner_profile:
                    SWIPE_COUNT = 1
                    today_first_transaction = Transaction(
                        owner=owner_profile,
                        authorizer=owner_profile,
                        swipe_count=SWIPE_COUNT,
                        reader_uid=reader_uid,
                        access_point=ACCESS_POINT,
                        raw_payload=reader_message,
                        grant_type=ACCESS_GRANTED,
                    )
                    today_first_transaction.save()
                    # client.publish(TOPIC, ACCESS_GRANTED)
                    print("***->RETURNING....Created TRANSACTION:", today_first_transaction)
                    return
        else:
            client.publish(TOPIC, ACCESS_DENIED)
            print("User not found!")

client.on_message = on_message
client.subscribe(TOPIC)
client.loop_forever()

import json
from django.utils import timezone
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
import paho.mqtt.publish as mqtt_publish
from users.models import UserProfile
from utils.utils import publish_data, is_card_reader_json

# Create your models here.


class Transaction(models.Model):
    swipe_count = models.IntegerField(default=0)
    reader_uid = models.CharField(max_length=128)
    date = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        UserProfile, related_name="user_transactions", on_delete=models.CASCADE
    )
    authorizer = models.ForeignKey(
        UserProfile, related_name="opener", on_delete=models.CASCADE
    )
    access_point = models.CharField(max_length=25)
    raw_payload = models.JSONField()
    door = models.CharField(max_length=128, blank=True, null=True)
    grant_type = models.CharField(max_length=25)

    def __str__(self):
        return f"Transaction-{self.owner.user.username}"


@receiver(post_save, sender=Transaction)
def on_save_signal_event(*args, **kwargs):
    TOPIC = "orinlakantobad"
    ACCESS_GRANTED = "ACCESS GRANTED"
    ACCESS_DENIED = "ACCESS DENIED"
    mqtt_broker = "broker.hivemq.com"
    print(
        "transaction.model.py#$#$#$#$#$#$#$# Transaction signal: Kwargs",
        kwargs["instance"].grant_type,
    )
    grant_type = kwargs["instance"].grant_type
    reader_uid = kwargs["instance"].reader_uid
    try:
        if grant_type == ACCESS_GRANTED:
            data = json.dumps(publish_data(ACCESS_GRANTED, uid=reader_uid))
            mqtt_publish.single(
                TOPIC,
                payload=data,
                hostname=mqtt_broker,
            )
        if grant_type == ACCESS_DENIED:
            data = json.dumps(publish_data(ACCESS_DENIED, uid=reader_uid))
            mqtt_publish.single(
                TOPIC,
                payload=data,
                hostname=mqtt_broker,
            )
    except Exception as e:
        print("Mqtt Publish Error:", e.args[0])

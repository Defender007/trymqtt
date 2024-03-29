# Generated by Django 3.2.23 on 2024-01-06 14:54

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.utils.timezone import utc
import json

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_userprofile_reader_uid'),
        ('core', '0004_alter_transaction_swipe_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='access_point',
            field=models.CharField(default="local", max_length=25),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='created_by',
            field=models.ForeignKey(default="b3c9f73e0cc74545b87f54537593622f", on_delete=django.db.models.deletion.CASCADE, related_name='opener', to='users.userprofile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='raw_payload',
            field=models.JSONField(default=json.dumps({"uid":"123456789"})),
            preserve_default=False,
        ),
    ]

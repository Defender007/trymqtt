# Generated by Django 3.2.23 on 2024-01-03 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_transaction_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='swipe_count',
            field=models.IntegerField(default=0),
        ),
    ]

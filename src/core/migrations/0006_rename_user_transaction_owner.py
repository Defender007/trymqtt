# Generated by Django 3.2.23 on 2024-01-07 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20240106_1454'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='user',
            new_name='owner',
        ),
    ]
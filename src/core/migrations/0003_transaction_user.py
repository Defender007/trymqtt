# Generated by Django 3.2.23 on 2024-01-02 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_username'),
        ('core', '0002_alter_transaction_reader_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_transactions', to='users.userprofile'),
            preserve_default=False,
        ),
    ]

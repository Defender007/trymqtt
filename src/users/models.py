import os
import random
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser


def generate_uid():
    random_string = "".join(random.choices("0123456789ABCDEFGHIJKLMNPRSTVWXYZ", k=10))
    print(random_string)
    return random_string

def upload_image(instance,filename ):
    return os.path.join('images', 'avatars', str(instance.pk), filename)

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=255,unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']


class UserProfile(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reader_uid = models.CharField(max_length=128, default=generate_uid, unique=True)
    profile_image = models.ImageField(upload_to=upload_image, blank=True, null=True)
    meal_category = models.PositiveSmallIntegerField(default=1)
    department = models.CharField(max_length=225)

    def __str__(self) -> str:
        return self.user.username

    
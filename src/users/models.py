import os

from uuid import uuid4
from django.core.exceptions import BadRequest
from django.db import models
from django.contrib.auth.models import AbstractUser


def upload_image(instance,filename ):
    return os.path.join('images', 'avatars', str(instance.pk), filename)

def upload_xlsx(instance, filename):
    base, extension = os.path.splitext(filename)
    if base.lower() != 'employee_batch' and extension.lower() !="xlsx":
        return BadRequest("Invalid File-type uploaded. File name must be 'employee_batch.xlsx'")
    return f"workbooks/{str(filename)}"
    # return os.path.join( 'workbooks', str(filename )



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
    reader_uid = models.CharField(max_length=128, unique=True)
    profile_image = models.ImageField(upload_to=upload_image, blank=True, null=True)
    meal_category = models.PositiveSmallIntegerField(default=1)
    department = models.CharField(max_length=225)

    def __str__(self) -> str:
        return self.user.username


class EmployeeBatchUpload(models.Model):
    batch_file = models.FileField(upload_to=upload_xlsx, blank=True, null=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self)-> str:
        return self.uploaded_by.username

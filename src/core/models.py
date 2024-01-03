from django.utils import timezone
from django.db import models
from users.models import UserProfile

# Create your models here.

class Transaction(models.Model):
    swipe_count = models.IntegerField(default=0)
    reader_uid = models.CharField(max_length=128)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(UserProfile, related_name='user_transactions',on_delete=models.CASCADE)
    
def __str__(self):
    return f'transaction-{self.reader_uid}'
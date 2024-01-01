from django.utils import timezone
from django.db import models

# Create your models here.

class Transaction(models.Model):
    swipe_count = models.IntegerField()
    reader_uid = models.CharField(max_length=128)
    date = models.DateTimeField(default=timezone.now)
    
def __str__(self):
    return f'transaction-{self.reader_uid}'
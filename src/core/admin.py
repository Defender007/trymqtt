from django.contrib import admin
from .models import Transaction



# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    pass
# Register your models here.
admin.site.register(Transaction, TransactionAdmin)
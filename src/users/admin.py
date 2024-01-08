from django.contrib import admin
from .models import User, UserProfile

class UserAdmin(admin.ModelAdmin):
    pass
# Register your models here.
admin.site.register(User, UserAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    pass
# Register your models here.
admin.site.register(UserProfile, UserProfileAdmin)
from django.contrib import admin
from .models import User, UserProfile, EmployeeBatchUpload

class UserAdmin(admin.ModelAdmin):
    pass
# Register your models here.
admin.site.register(User, UserAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    pass
# Register your models here.
admin.site.register(UserProfile, UserProfileAdmin)


class EmployeeBatchUploadAdmin(admin.ModelAdmin):
    pass
# Register your models here.
admin.site.register(EmployeeBatchUpload, EmployeeBatchUploadAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# إلغاء التسجيل القديم وإعادة تسجيل User بإضافة ProfileInline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


#python3 manage.py runserver
#python3 manage.py makemigrations
#python3 manage.py migrate
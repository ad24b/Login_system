from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True, verbose_name="رقم الجوال")

    def __str__(self):
        return f"{self.user.username} - {self.phone}"


#python3 manage.py runserver
#python3 manage.py makemigrations
#python3 manage.py migrate
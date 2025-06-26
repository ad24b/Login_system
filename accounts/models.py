# models.py
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.user.username


#python3 manage.py runserver
#python3 manage.py makemigrations
#python3 manage.py migrate
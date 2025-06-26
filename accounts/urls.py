from django.urls import path
from . import views

urlpatterns = [
    path('phone-login/', views.phone_login, name='phone_login'),
    path('verify/', views.verify_otp, name='verify_otp'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register_user'),
    path('check-user/', views.check_user_exists, name='check_user_exists'),
    path('start-registration/', views.start_registration, name='start_registration'),
    



]
# python3 manage.py runserver
#python3 manage.py makemigrations
#python3 manage.py migrate
from django.urls import path
from . import views

urlpatterns = [
    path('phone-login/', views.phone_login, name='phone_login'),
    path('verify/', views.verify_otp, name='verify_otp'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.home, name='home'),
]

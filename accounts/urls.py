from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('otp-login/', views.otp_login, name='otp_login'),
]
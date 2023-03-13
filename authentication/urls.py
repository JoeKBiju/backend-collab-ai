from django.urls import path
from .views import register, login, user_details, logout, change_name, change_email, change_password

urlpatterns = [
    path('register', register),
    path('login', login),
    path('user-details', user_details),
    path('logout', logout),
    path('change-name', change_name),
    path('change-email', change_email),
    path('change-password', change_password)
]


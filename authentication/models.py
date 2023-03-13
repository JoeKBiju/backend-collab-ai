from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(max_length=250, unique=True, name='email')
    name = models.CharField(max_length=250, name='name')
    password = models.CharField(max_length=250, name='password')
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
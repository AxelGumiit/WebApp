from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal


class CustomUser(AbstractUser):
    Currency_Choices = [
        ('GBP', 'Great Britain Pounds'),
        ('USD', 'United States Dollars'),
        ('EUR', 'Euro'),
    ]
   
    email = models.EmailField(unique=True, blank=False)
    currency = models.CharField(max_length=10, choices=Currency_Choices)
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=750)

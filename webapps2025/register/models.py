from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class CurrencyChoices(forms.ChoiceField):
    GBP = 'GBP', 'GBP'
    USD = 'USD', 'USD'
    EUR = 'EUR', 'EUR'

    CURRENCY_CHOICES = [
        ('GBP', 'GBP'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    ]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', self.CURRENCY_CHOICES)
        super().__init__(*args, **kwargs)



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    currency = forms.ChoiceField(choices=CurrencyChoices.CURRENCY_CHOICES, required=True, label="Currency")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2", "currency")



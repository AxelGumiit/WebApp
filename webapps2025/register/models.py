from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    currency = forms.ChoiceField(
        choices=[('GBP', 'GBP'), ('USD', 'USD'), ('EUR', 'EUR')], 
        required=True, 
        label="Currency"
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2", "currency")

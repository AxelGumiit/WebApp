from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth.forms import AuthenticationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    currency = forms.ChoiceField(
        choices=[('GBP', 'GBP'), ('USD', 'USD'), ('EUR', 'EUR')], 
        required=True, 
        label="Currency"
    )
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "password1", "password2", "currency")


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your username"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter your password"}),
    )

    class Meta:
        fields = ["username", "password"]




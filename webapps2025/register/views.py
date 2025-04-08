from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db import transaction
import requests

@transaction.atomic()
def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()

            # Get the selected currency
            currency = form.cleaned_data['currency']

            # Default balance
            default_balance = 750

            # Currency conversion logic
            if currency != 'GBP':
                conversion_url = f"http://127.0.0.1:8000/currency/conversion/GBP/{currency}/{default_balance}/"
                try:
                    response = requests.get(conversion_url)

                    if response.status_code == 200:
                        data = response.json()
                        converted_amount = data['converted_amount']
                        user.balance = converted_amount
                    else:
                        # If the conversion API fails, use the default balance
                        user.balance = default_balance

                except requests.exceptions.RequestException as e:
                    # In case of an error, use the default balance
                    user.balance = default_balance
                    print(f"Error calling currency conversion API: {e}")
            else:
                # If currency is GBP, use the default balance
                user.balance = default_balance

            # Save the user with the updated balance
            user.save()

            # Log the user in
            login(request=request, user=user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, f'Account created for {user.username}!')

            # Redirect to the payapp page
            return redirect('../payapp')
    else:
        form = RegisterForm()

    return render(request, 'register/register.html', {'register_user': form})

def login_user(request):
    if request.method == "POST":
        form = LoginForm(request, request.POST)  

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
   
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                if user.is_superuser:  # Redirect superuser to the admin page
                    messages.info(request, f"You are now logged in as {username} (Superuser).")
                    return redirect("../payapp/admin") 
                else:
                    messages.info(request, f"You are now logged in as {username}.")
                    return redirect("../payapp")  

            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    else:
        form = LoginForm()

    return render(request, "register/login.html", {"login_user": form})

def logout_user(request):
    logout(request)  
    request.session.flush()
    return redirect('/login/')  

from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from register.models import RegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages


def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Get the selected currency from the form
            selected_currency = form.cleaned_data.get('currency')

            # Set the initial balance in GBP
            initial_balance = 750  # £750 as the baseline value

            # Convert to the selected currency
            if selected_currency == 'GBP':
                balance = initial_balance
            elif selected_currency == 'USD':
                # Assuming £1 = $1.3
                balance = initial_balance * 1.3
            elif selected_currency == 'EUR':
                # Assuming £1 = €1.2
                balance = initial_balance * 1.2
            else:
                balance = initial_balance  # Default to GBP if something unexpected happens

            # Create the UserProfile with the initial balance
            user_profile = UserProfile(user=user, currency=selected_currency, balance=balance)
            user_profile.save()

            messages.success(request, "Registration successful.")
            return redirect("../payapp")  # Redirect to payapp homepage or dashboard

        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = RegisterForm()

    return render(request, "register/register.html", {"register_user": form})


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("../payapp")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, "register/login.html", {"login_user": form})


def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("login")

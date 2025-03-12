from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from register.models import RegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from payapp.models import UserProfile


def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()

            # Create and save the UserProfile with the selected currency
            currency = form.cleaned_data['currency']
            user_profile = UserProfile.objects.create(user=user, balance=0.00, currency=currency)

            # Log the user in after registration
            login(request, user)

            messages.success(request, f'Account created for {user.username}!')
            return redirect('../payapp')  
    else:
        form = RegisterForm()

    return render(request, 'register/register.html', {'register_user': form})

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

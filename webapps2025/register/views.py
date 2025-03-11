from django.shortcuts import render

path("register/", register_views.register_user, name="register")
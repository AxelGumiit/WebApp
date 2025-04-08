from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import register_user, login_user, logout_user

urlpatterns = [
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"), 
    path("logout/", logout_user, name="logout"), 
    path("accounts/", include("django.contrib.auth.urls")),
]

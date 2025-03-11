from django.urls import path
from .views import *

urlpatterns = [
    path("payapp/", home,  name="Home"),

]
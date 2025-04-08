
from django.contrib import admin
from django.urls import include, path
from payapp.views import startup_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', startup_page, name='Payapp'),
    path('', include("register.urls")),
    path('', include("payapp.urls")),
    path('currency/', include('currency_converter.urls')),                 

]

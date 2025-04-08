
from django.contrib import admin
from django.urls import include, path
from payapp.views import startup_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webapps2025/', startup_page, name='Payapp'),
    path('webapps2025/', include("register.urls")),
    path('webapps2025/', include("payapp.urls")),
    path('webapps2025/', include('currency_converter.urls')),

]

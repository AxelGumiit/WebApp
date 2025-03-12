from django.contrib import admin
from register.views import register_user 
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('a', register_user, name='register'),
    path('', include("register.urls")),
    path('', include("payapp.urls"))                     

]

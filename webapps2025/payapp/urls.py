from django.urls import path
from .views import *

urlpatterns = [
    path("payapp/", home,  name="Home"),
    path('mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path("payapp/admin", admin_dashboard, name="Admin"),
]

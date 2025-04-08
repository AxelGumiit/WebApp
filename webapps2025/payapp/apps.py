# payapp/apps.py
from django.apps import AppConfig

class PayappConfig(AppConfig):
    name = 'payapp'

    def ready(self):
        import payapp.signals

from django.urls import path
from .views import CurrencyConversionAPIView

urlpatterns = [
    path('conversion/<str:from_currency>/<str:to_currency>/<str:amount>/', CurrencyConversionAPIView.as_view(), name='currency_conversion'),
]
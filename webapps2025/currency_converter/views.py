from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
from decimal import Decimal, ROUND_HALF_UP


class CurrencyConversionAPIView(APIView):
    exchange_rates = {
        'GBP': {'USD': 1.3, 'EUR': 1.2, 'GBP': 1.0},
        'USD': {'GBP': 0.77, 'EUR': 0.92, 'USD': 1.0},
        'EUR': {'GBP': 0.83, 'USD': 1.09, 'EUR': 1.0},
    }

    def get(self, request, from_currency, to_currency, amount):
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()

            if from_currency not in self.exchange_rates or to_currency not in self.exchange_rates[from_currency]:
                return JsonResponse({'error': 'Unsupported currency or conversion'}, status=status.HTTP_400_BAD_REQUEST)

            amount_decimal = Decimal(amount)
            if amount_decimal < 0:
                return JsonResponse({'error': 'Amount must be non-negative'}, status=status.HTTP_400_BAD_REQUEST)

            conversion_rate = Decimal(self.exchange_rates[from_currency][to_currency]).quantize(Decimal('0.01'),
                                                                                                rounding=ROUND_HALF_UP)
            converted_amount = amount_decimal * conversion_rate
            converted_amount_quantized = converted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            return JsonResponse({
                'from_currency': from_currency,
                'to_currency': to_currency,
                'conversion_rate': str(conversion_rate),
                'amount': str(amount_decimal),
                'converted_amount': str(converted_amount_quantized)
            })

        except Exception:
            return JsonResponse({'error': 'Invalid request'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

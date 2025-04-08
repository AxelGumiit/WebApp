from django.urls import path
from .views import *

urlpatterns = [
    path("payapp/", home, name="Home"),
    path('mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path("payapp/admin", admin_dashboard, name="Admin"),
    path('payapp/sent_money', send_money, name='send_money'),
    path('confirm_send_money/', confirm_send_money, name='confirm_send_money'),
    path('payapp/startUp', startup_page, name='Payapp'),
    path('request_payment/', request_payment, name='request_payment'),
    path('payment_requests/', view_payment_requests, name='payment_requests'),
    path('payment_request/accept/<int:request_id>/', accept_payment_request, name='accept_payment_request'),
    path('payment_request/reject/<int:request_id>/', reject_payment_request, name='reject_payment_request'),
    path('payapp/admin/create/', create_admin, name='create_admin'),
    path('payapp/admin/transactions/', all_transactions, name='all_transactions'),
    path('notifications/', notifications, name='notifications'),
    path('notifications/mark_all_as_read/', mark_all_as_read, name='mark_all_as_read'),

]
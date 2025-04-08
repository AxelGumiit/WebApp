from django.db import models
from register.models import CustomUser
from django.contrib.auth import get_user_model


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, choices=[
        ('send_money', 'Send Money'),
        ('receive_money', 'Receive Money'),
        ('payment_request', 'Payment Request'),
        ('other', 'Other')
    ], default='other')

    def __str__(self):
        return f"[{self.notification_type}] {self.message}"


class Transaction(models.Model):
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)  # e.g., GBP, USD, EUR
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_request = models.ForeignKey('PaymentRequest', on_delete=models.CASCADE, related_name='transactions',
                                        null=True, blank=True)
    original_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                          blank=True)  # New field for original amount
    original_currency = models.CharField(max_length=3, null=True, blank=True)

    def __str__(self):
        return f"Transaction from {self.sender.username} to {self.recipient.username}"

    def get_transaction_amount(self):
        if self.payment_request:
            return self.original_amount  # Return the original amount if it's a payment request
        return self.amount


class PaymentRequest(models.Model):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    sender = models.ForeignKey(CustomUser, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_requests', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    converted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Request from {self.sender} to {self.receiver} for {self.amount} {self.receiver.currency}"

    def is_accepted(self):
        return self.status == self.ACCEPTED

    def is_rejected(self):
        return self.status == self.REJECTED
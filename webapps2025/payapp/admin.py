
from django.contrib import admin
from .models import Notification, Transaction, PaymentRequest



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    model = Notification
    list_display = [field.name for field in Notification._meta.fields]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = ('sender', 'recipient', 'amount', 'currency', 'created_at', 'description')
    list_filter = ('currency', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'currency')
    ordering = ('-created_at',) 
    date_hierarchy = 'created_at'  


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    model = PaymentRequest
    list_display = ('sender', 'receiver', 'amount', 'status', 'created_at')  
    list_filter = ('status', 'created_at') 
    search_fields = ('sender__username', 'receiver__username', 'status')  
    ordering = ('-created_at',) 
    date_hierarchy = 'created_at' 
    actions = ['accept_requests', 'reject_requests'] 

    # Define custom actions for accepting or rejecting payment requests
    def accept_requests(self, request, queryset):
        queryset.update(status=PaymentRequest.ACCEPTED)
        self.message_user(request, f'{queryset.count()} requests have been accepted.')

    accept_requests.short_description = 'Accept selected payment requests'

    def reject_requests(self, request, queryset):
        queryset.update(status=PaymentRequest.REJECTED)
        self.message_user(request, f'{queryset.count()} requests have been rejected.')

    reject_requests.short_description = 'Reject selected payment requests'
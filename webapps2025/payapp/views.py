from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.db.models import Q
from decimal import Decimal
import requests
from django.http import Http404
from .models import Transaction, CustomUser, PaymentRequest, Notification
from .forms import TransactionForm, AdminUserForm


def is_superuser(user):
    """Check if the user is a superuser"""
    return user.is_authenticated and user.is_superuser


def startup_page(request):
    return render(request, 'payapp/startUp.html')


@login_required
def home(request):
    """User dashboard with balance, recent transactions, and notifications."""
    user = request.user
    transactions = Transaction.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).select_related("sender", "recipient").order_by("-created_at")[:10]

    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:10]
    unread_notifications_count = Notification.objects.filter(user=user, read=False).count()

    return render(request, "payapp/home.html", {
        'notifications': notifications,
        'currency': user.currency,
        'balance': user.balance,
        'transactions': transactions,
        'unread_notifications_count': unread_notifications_count
    })


@login_required
@transaction.atomic
def send_money(request):
    """Handles sending money transactions."""
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:10]
    unread_notifications_count = Notification.objects.filter(user=user, read=False).count()

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            sender = request.user
            recipient_email = form.cleaned_data['recipient_email']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '')

            recipient = CustomUser.objects.filter(email=recipient_email).first()
            if not recipient:
                messages.error(request, "No user found with this email.")
                return redirect('send_money')

            # Currency conversion
            amount_in_recipient_currency = amount
            if sender.currency != recipient.currency:
                conversion_url = f"http://127.0.0.1:8000/currency/conversion/{sender.currency}/{recipient.currency}/{amount}/"
                try:
                    response = requests.get(conversion_url).json()
                    amount_in_recipient_currency = Decimal(response.get('converted_amount', amount))
                except Exception:
                    messages.error(request, "Currency conversion failed.")
                    return redirect('send_money')

            # Store details in session for confirmation
            request.session['recipient_email'] = recipient_email
            request.session['amount'] = float(amount)  # Convert Decimal to float
            request.session['amount_in_recipient_currency'] = float(
                amount_in_recipient_currency)  # Convert Decimal to float
            request.session['recipient_currency'] = recipient.currency
            request.session['description'] = description

            # Redirect to confirmation page
            return redirect('confirm_send_money')



    else:
        form = TransactionForm()

    return render(request, 'payapp/send_money.html', {
        'form': form,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count
    })


@login_required
@transaction.atomic
def confirm_send_money(request):


    sender = request.user
    recipient_email = request.session.get('recipient_email')

    if not recipient_email:
        messages.error(request, "Invalid transaction session. Please try again.")
        return redirect('send_money')

    recipient = get_object_or_404(CustomUser, email=recipient_email)
    amount_in_recipient_currency = Decimal(request.session['amount_in_recipient_currency'])
    recipient_currency = request.session['recipient_currency']
    description = request.session['description']
    amount = Decimal(request.session['amount'])

    if request.method == 'POST':

        if sender.balance >= amount_in_recipient_currency:

            amount_in_recipient_currency_2dp = amount_in_recipient_currency.quantize(Decimal('0.01'))
            amount = amount.quantize(Decimal('0.01'))
            transaction = Transaction.objects.create(
                sender=sender,
                recipient=recipient,
                amount=amount_in_recipient_currency_2dp,
                currency=recipient_currency,
                description=description,
                original_amount=amount,
                original_currency=sender.currency,
            )


            sender.balance -= amount
            recipient.balance += amount_in_recipient_currency_2dp
            sender.save()
            recipient.save()

            Notification.objects.bulk_create([
                Notification(user=recipient,
                             message=f"You received {amount_in_recipient_currency_2dp} {recipient_currency} from {sender.username}. Description: {description}",
                             notification_type="receive_money"),
                Notification(user=sender,
                             message=f"You sent {amount} {sender.currency } to {recipient.username}. Description: {description}",
                             notification_type="sent_money"),
            ])

            for key in ['recipient_email', 'amount', 'amount_in_recipient_currency', 'recipient_currency',
                        'description']:
                request.session.pop(key, None)

            messages.success(request,
                             f"Payment of {amount_in_recipient_currency} {recipient_currency} sent to {recipient.username} successfully!")
            return redirect('../payapp')
        else:
            messages.error(request, "You do not have enough balance to make this payment.")
            return redirect('send-money')



    return render(request, 'payapp/confirm_send_money.html', {
        'amount_in_recipient_currency': amount_in_recipient_currency.quantize(Decimal('0.01')),
        'recipient_username': recipient.username,
        'recipient_currency': recipient_currency,
        'description': description,
        'original_amount': amount,
    })


@login_required
def notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_notifications_count = Notification.objects.filter(user=user, read=False).count()
    return render(request, 'payapp/notifications.html', {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count
    })


def mark_all_as_read(request):
    if request.user.is_authenticated:

        unread_notifications = Notification.objects.filter(user=request.user, read=False)
        unread_notifications.update(read=True)

    return redirect('notifications')


@login_required
def mark_as_read(request, notification_id):

    notification = get_object_or_404(Notification, id=notification_id, user=request.user)

    notification.read = True
    notification.save()


    if notification.notification_type == "payment_request":
        return redirect('payment_requests')
    else:
        return redirect('notifications')

@login_required
@transaction.atomic
def request_payment(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:10]
    unread_notifications_count = Notification.objects.filter(user=user, read=False).count()
    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email')
        amount = request.POST.get('amount')
        description = request.POST.get('description')

        if not recipient_email or not amount:
            messages.error(request, "Recipient and amount are required.")
            return redirect('request_payment')

        try:
            recipient = CustomUser.objects.get(email=recipient_email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Recipient does not exist.")
            return redirect('request_payment')

        if recipient == request.user:
            messages.error(request, "You cannot request money from yourself.")
            return redirect('request_payment')


        sender_currency = request.user.currency
        receiver_currency = recipient.currency
        amount_in_receiver_currency = Decimal(amount)

        if sender_currency != receiver_currency:
            conversion_url = f"http://127.0.0.1:8000/currency/conversion/{sender_currency}/{receiver_currency}/{amount}/"
            try:
                response = requests.get(conversion_url)
                if response.status_code == 200:
                    data = response.json()
                    amount_in_receiver_currency = Decimal(data['converted_amount'])
                    print(f"Converted {amount} {sender_currency} to {amount_in_receiver_currency} {receiver_currency}")
                else:
                    messages.error(request, "Error occurred during currency conversion.")
                    return redirect('request_payment')
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error occurred during API call: {e}")
                return redirect('request_payment')


        payment_request = PaymentRequest.objects.create(
            sender=request.user,
            receiver=recipient,
            amount=amount,
            status=PaymentRequest.PENDING,
            description=description,
            converted_amount=amount_in_receiver_currency
        )


        payment_request_url = reverse('accept_payment_request', args=[payment_request.id])

        Notification.objects.bulk_create([
            Notification(
                user=recipient,
                message=f"You have received a payment request of {amount_in_receiver_currency} {receiver_currency} from {request.user.username}. Description: {description}",
                link=payment_request_url,
                notification_type="payment_request"
            ),
            Notification(
                user=request.user,
                message=f"You have sent a payment request of  {amount} {sender_currency} to {recipient.username}. Description: {description}",
                link=payment_request_url,
                notification_type="payment_request"
            )
        ])

        messages.success(request,
                         f"Payment request of {amount_in_receiver_currency} {receiver_currency} sent to {recipient.username}.")
        return redirect('/payment_requests')

    users = CustomUser.objects.exclude(id=request.user.id)
    return render(request, 'payapp/request_payment.html', {
        'users': users,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count
    })


@login_required
def view_payment_requests(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:10]
    unread_notifications_count = Notification.objects.filter(user=user, read=False).count()

    if not request.user.is_authenticated:
        raise Http404("Page not found")


    received_requests = PaymentRequest.objects.filter(
        receiver=request.user,
        status=PaymentRequest.PENDING
    )


    sent_requests = PaymentRequest.objects.filter(
        sender=request.user,
        status__in=[PaymentRequest.PENDING, PaymentRequest.ACCEPTED, PaymentRequest.REJECTED]
    )

    accepted_or_rejected_requests = PaymentRequest.objects.filter(
        receiver=request.user,
        status__in=[PaymentRequest.ACCEPTED, PaymentRequest.REJECTED]
    )


    return render(request, 'payapp/payment_requests_list.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
        'accepted_or_rejected_requests': accepted_or_rejected_requests,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count
    })


@login_required
@transaction.atomic
def accept_payment_request(request, request_id):
    payment_request = get_object_or_404(PaymentRequest, id=request_id)

    if payment_request.receiver != request.user:
        raise Http404("You are not authorized to accept this payment request.")

    sender = payment_request.sender
    receiver = payment_request.receiver
    amount = Decimal(payment_request.amount)


    if sender.currency != receiver.currency:
        conversion_url = f"http://127.0.0.1:8000/currency/conversion/{sender.currency}/{receiver.currency}/{amount}/"
        try:
            response = requests.get(conversion_url)
            if response.status_code == 200:
                data = response.json()
                amount_in_receiver_currency = Decimal(data['converted_amount'])

                print(f"Converted {amount} {sender.currency} to {amount_in_receiver_currency} {receiver.currency}")
            else:
                messages.error(request, "Error occurred during currency conversion.")
                return redirect('payment_requests')
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error occurred during API call: {e}")
            return redirect('payment_requests')
    else:

        amount_in_receiver_currency = amount

    if receiver.balance < amount_in_receiver_currency:
        messages.error(request, "You do not have enough balance to accept this payment request.")
        return redirect('payment_requests')


    receiver.balance -= amount_in_receiver_currency
    receiver.save()

    sender.balance += amount
    sender.save()


    # Update the payment request status to ACCEPTED
    payment_request.status = PaymentRequest.ACCEPTED
    payment_request.save()

    transaction = Transaction.objects.create(
        sender=receiver,
        recipient=sender,
        original_amount=amount,
        original_currency=sender.currency,
        amount=amount_in_receiver_currency,
        currency=receiver.currency,
        payment_request=payment_request
    )


    notification_message_sender = f"Your payment request has been accepted by {receiver.username}."
    Notification.objects.create(user=sender, message=notification_message_sender)

    notification_message_receiver = f"You have sent {amount_in_receiver_currency} {receiver.currency} to {sender.username}."
    Notification.objects.create(user=receiver, message=notification_message_receiver)


    messages.success(request,
                     f"You have accepted the payment request from {payment_request.sender.username} and transferred {amount_in_receiver_currency} {receiver.currency}.")
    return redirect('/payapp/')


@login_required
def reject_payment_request(request, request_id):
    payment_request = get_object_or_404(PaymentRequest, id=request_id)

    if payment_request.receiver != request.user:
        raise Http404("You are not authorized to reject this payment request.")

    payment_request.status = PaymentRequest.REJECTED
    payment_request.save()

    notification_message_sender = f"Your payment have been rejected by {payment_request.receiver.username}."
    Notification.objects.create(user=payment_request.sender, message=notification_message_sender)


    messages.success(request, f"You have rejected the payment request from {payment_request.sender.username}.")
    return redirect('payment_requests')


@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    users = CustomUser.objects.all()
    transactions = Transaction.objects.all().select_related('sender', 'recipient').order_by('-created_at')

    return render(request, 'payapp/admin.html', {
        'users': users, 'transactions': transactions
    })


@login_required
@user_passes_test(is_superuser)
def all_transactions(request):
    if request.user.is_authenticated and request.user.is_superuser:
        transactions = Transaction.objects.all().select_related('sender', 'recipient').order_by('-created_at')

        for t in transactions:
            print(
                f"Transaction ID: {t.id}, Amount: {t.amount}, Sender: {t.sender.username}, Recipient: {t.recipient.username}")

        return render(request, 'payapp/all_transaction.html', {'transactions': transactions})
    else:
        return redirect('login')


@login_required
@user_passes_test(is_superuser)
@transaction.atomic
def create_admin(request):
    """Allows superusers to create new admin users."""
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_superuser = True
            new_user.is_staff = True
            new_user.save()
            messages.success(request, f"New admin '{new_user.username}' created successfully.")
            return redirect('Admin')

    else:
        form = AdminUserForm()

    return render(request, 'payapp/create_admin.html', {'form': form})
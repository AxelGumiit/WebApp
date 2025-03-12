from django.shortcuts import render
from .models import Notification
from django.shortcuts import get_object_or_404, redirect

def home(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        balance = 750 
    else:
        notifications = []
        balance = 750

    return render(request, "payapp/home.html", {'notifications': notifications, 'balance': balance,})




def mark_as_read(request, notification_id):

    notification = get_object_or_404(Notification, id=notification_id)


    if notification.user == request.user:

        notification.read = True
        notification.save()


    return redirect('../payapp') 

def admin_dashboard(request):

    return render(request, 'payapp/admin.html')

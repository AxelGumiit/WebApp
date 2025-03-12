from django.shortcuts import render
from .models import Notification

def home(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = []

    return render(request, "payapp/home.html", {'notifications': notifications})

from django.shortcuts import get_object_or_404, redirect
from .models import Notification

def mark_as_read(request, notification_id):

    notification = get_object_or_404(Notification, id=notification_id)


    if notification.user == request.user:

        notification.read = True
        notification.save()


    return redirect('../payapp') 

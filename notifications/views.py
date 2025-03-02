from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification

# Create your views here.
@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(username=request.user).order_by('-created_at')
    notifications_list = [
        {
            'type': notification.type,
            'data': notification.data,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for notification in notifications
    ]
    return JsonResponse(notifications_list, safe=False)

@login_required
def get_unread_notifications_count(request):
    unread_count = Notification.objects.filter(username=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})
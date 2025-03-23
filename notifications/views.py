from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification
from communities.models import Communities
from django.contrib import messages

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
def get_unread_notifications(request):
    notifications = Notification.objects.filter(username=request.user, is_read=False).order_by('-created_at')
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

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(username=request.user).order_by('-created_at')
    return render(request, 'notifications/notifications.jinja', {'notifications': notifications})

@login_required
def mark_all_as_read(request):
    if request.method == "POST":
        Notification.objects.filter(username=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def approve_community(request, community_id: str):
    if not request.user.is_superuser:
        return JsonResponse(status=403)
    
    community = get_object_or_404(Communities, id=community_id)
    community.status = 'approved'
    community.save()
    messages.success(request, f"Community '{community.name}' has been approved.")
    return redirect("community_list")

@login_required
def reject_community(request, community_id: str):
    if not request.user.is_superuser:
        return JsonResponse(status=403)
    
    community = get_object_or_404(Communities, id=community_id)
    community.status = 'rejected'
    community.delete()
    messages.success(request, f"Community '{community.name}' has been rejected.")
    return redirect("community_list")
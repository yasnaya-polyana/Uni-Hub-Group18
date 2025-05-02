from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification
from communities.models import Communities, CommunityMember
from django.contrib import messages
from notifications.manager import NotificationManager
from accounts.models import CustomUser

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
    # Get notifications for the logged-in user (using username FK)
    notifications = Notification.objects.filter(username=request.user).order_by('-created_at')

    # Attach follower_user object based on follower_username in JSON data
    for notification in notifications:
        follower_username = notification.data.get("follower_username")
        if follower_username:
            try:
                notification.follower_user = CustomUser.objects.get(username=follower_username)
            except CustomUser.DoesNotExist:
                notification.follower_user = None
        else:
            notification.follower_user = None

    return render(request, 'notifications/notifications.jinja', {
        'notifications': notifications
    })

@login_required
def mark_all_as_read(request):
    if request.method == "POST":
        Notification.objects.filter(username=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def approve_community(request, community_id: str):
    if not request.user.is_superuser:
        return JsonResponse({"error": "You do not have permission to approve communities."}, status=403)
    
    try:
        # Attempt to retrieve the community
        community = Communities.objects.get(id=community_id)
    except Communities.DoesNotExist:
        # Handle the case where the community does not exist so remove it
        Notification.objects.filter(data__community_id=community_id).delete() 
        
        messages.error(request, "The community you are trying to approve does not exist.")
        return redirect("community_list")  # Redirect to a safe page, e.g., the community list
    
    # Approve the community
    community.status = 'approved'
    community.save()
    
    # Notify the owner about the approval decision
    NotificationManager.community_decision(
        owner=community.owner,
        community=community,
        decision='approved'
    )
    
    # Update the notification related to this community
    notification = Notification.objects.filter(data__community_id=community.id).first()
    if notification:
        notification.is_interact = True
        notification.save()
    
    # Add a success message and redirect
    messages.success(request, f"Community '{community.name}' has been approved.")
    return redirect("community_list")

@login_required
def reject_community(request, community_id: str):
    if not request.user.is_superuser:
        return JsonResponse(status=403)
    
    community = get_object_or_404(Communities, id=community_id)
    community.status = 'rejected'
    community.delete()
    
    NotificationManager.community_decision(
        owner=community.owner,
        community=community,
        decision='rejected'
    )
    
    notification = Notification.objects.filter(data__community_id=community.id).first()
    if notification:
        notification.is_interact = True
        notification.save()
    
    messages.success(request, f"Community '{community.name}' has been rejected.")
    return redirect("community_list")

@login_required
def approve_role(request, community_id: str, role: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    if not (user.is_superuser or user == community.owner or CommunityMember.objects.filter(user=user, community=community, role="moderator").exists()):
        return JsonResponse(status=403)

    membership = CommunityMember.objects.filter(community=community, role=f"pending_{role}").first()
    if membership:
        membership.role = role
        membership.save()
        
        NotificationManager.role_decision(
            requester=membership.user,
            community=community,
            role=role,
            decision='approved'
        )
        # TODO: bugfix required here
        # TODO: bugfix required here
        # TODO: bugfix required here
        
        notification = Notification.objects.filter(data__community_id=community_id, data__requested_role=role).first()
        if notification:
            notification.is_interact = True
            notification.save()
        messages.success(request, f"Role request for '{community.name}' has been approved.")
    else:
        messages.error(request, "No pending role request found.")

    return redirect("community_detail", community_id=community_id)

@login_required
def reject_role(request, community_id: str, role: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    if not (user.is_superuser or user == community.owner or CommunityMember.objects.filter(user=user, community=community, role="moderator").exists()):
        return JsonResponse(status=403)

    membership = CommunityMember.objects.filter(community=community, role=f"pending_{role}").first()
    if membership:
        membership.role = "subscriber" if role == "member" else "member"
        membership.save()
        
        NotificationManager.role_decision(
            requester=membership.user,
            community=community,
            role=role,
            decision='rejected'
        )
        
        notification = Notification.objects.filter(data__community_id=community_id, data__requested_role=role).first()
        if notification:
            notification.is_interact = True
            notification.save()
        messages.success(request, f"Role request for '{community.name}' has been rejected.")
    else:
        messages.error(request, "No pending role request found.")

    return redirect("community_detail", community_id=community_id)

@login_required
def community_accept_invite(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    # Check if already a member
    is_already_member = (
        CommunityMember.objects.filter(user=user, community=community).count() > 0
    )

    if is_already_member:
        messages.warning(request, "You are already a member of this community.")
    else:
        # Create membership with role="member" since it's from an invite
        CommunityMember.objects.create(user=user, community=community, role="member")
        messages.success(request, f"You have joined {community.name}!")
    
    # Mark notification as interacted with
    notification = Notification.objects.filter(
        username=user,
        type='community_invite',
        data__community_id=community_id,
        is_interact=False
    ).first()
    
    if notification:
        notification.is_interact = True
        notification.save()
    
    return redirect("notifications")

@login_required
def community_decline_invite(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    # Mark notification as interacted with
    notification = Notification.objects.filter(
        username=user,
        type='community_invite',
        data__community_id=community_id,
        is_interact=False
    ).first()
    
    if notification:
        notification.is_interact = True
        notification.save()
    
    messages.info(request, f"You declined the invitation to join {community.name}.")
    return redirect("notifications")
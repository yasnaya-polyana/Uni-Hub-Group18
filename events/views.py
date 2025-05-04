import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from communities.models import CommunityMember

from .models import Event


@login_required
def events_list(request):
    # Get all public events where the end time is in the future
    # Also filter to only include events where the community still exists and is approved
    events = Event.objects.filter(
        end_at__gte=datetime.date.today(),
        community__isnull=False,
        community__deleted_at__isnull=True,
        community__status='approved'
    ).order_by("start_at")
    
    # Filter out members-only events if not a member
    if request.user.is_authenticated:
        # Get user's communities
        user_community_ids = CommunityMember.objects.filter(
            user=request.user
        ).values_list('community', flat=True)
        
        # Filter events where the user is a member of the respective community
        members_events = [
            event for event in events
            if hasattr(event, 'community') and event.community and event.community.id in user_community_ids
        ]
    
    return render(request, "events/events.jinja", {"events": events, "members_events": members_events, "user": request.user})


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Check if the community still exists and is approved
    if not hasattr(event, 'community') or not event.community or hasattr(event.community, 'deleted_at') and event.community.deleted_at or event.community.status != 'approved':
        messages.error(
            request,
            "This event is no longer available because its community has been deleted or is not approved."
        )
        return redirect("events")
    
    # Check if event has members_only attribute and it's True
    if hasattr(event, 'members_only') and event.members_only:
        # Check if user is a member of the community
        is_member = CommunityMember.objects.filter(
            user=request.user,
            community=event.community
        ).exists()
        
        if not is_member and request.user != event.community.owner:
            messages.error(
                request,
                "This event is for community members only. Please join the community to view details."
            )
            return redirect("community_detail", community_id=event.community.id)
    
    return render(request, "events/event-detail.jinja", {"event": event})

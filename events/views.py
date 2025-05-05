from communities.models import CommunityMember
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Q
from django.http import HttpResponse  # For debugging
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from search.service import compile_query

from .forms import EventCreationForm
from .models import Event


@login_required
def events_list(request):
    # Get search query if available
    query_str = request.GET.get("q", "")

    # Create a subquery to check if the user is an active member of each event's community
    is_active_member = CommunityMember.objects.filter(
        user=request.user, community=OuterRef("community"), is_suspended=False
    )

    # Get all upcoming events
    events_query = Event.objects.filter(
        end_at__gte=timezone.now()  # Only show events that haven't ended
    ).annotate(user_is_active_member=Exists(is_active_member))

    # Filter events based on membership status and members_only flag
    events = events_query.filter(
        # Either the event is not members_only OR the user is an active member
        Q(members_only=False)
        | Q(members_only=True, user_is_active_member=True)
    ).order_by("start_at")

    # Apply search if query exists
    if query_str:
        compiled_query = compile_query(query_str)
        events = events.filter(
            Q(title__icontains=compiled_query)
            | Q(details__icontains=compiled_query)
            | Q(location__icontains=compiled_query)
            | Q(community__name__icontains=compiled_query)
        )

    context = {"events": events, "search_query": query_str}

    return render(request, "events/events-list.jinja", context)


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return redirect("post", post_id=event.post.id)

    # # Check if user is allowed to view this event
    # is_member = CommunityMember.objects.filter(
    #     user=request.user,
    #     community=event.community,
    #     is_suspended=False
    # ).exists()
    #
    # # If it's a members-only event and user is not a member, redirect
    # if event.members_only and not is_member:
    #     messages.error(request, "This event is only available to members of the community.")
    #     return redirect('events')
    #
    # return render(request, 'events/event-detail.jinja', {
    #     'event': event,
    #     'now': timezone.now()  # Pass the current time to the template
    # })


@login_required
def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if user has permission to edit (must be a moderator, owner, admin, or superuser)
    is_moderator = CommunityMember.objects.filter(
        user=request.user, community=event.community, role="moderator"
    ).exists()
    is_admin = request.user == event.community.owner
    is_superuser = request.user.is_superuser

    # Only allow moderators, community admins, and superusers to edit events
    if not (is_moderator or is_admin or is_superuser):
        messages.error(
            request,
            "Only moderators, community owners, and site admins can edit events.",
        )
        return redirect("event_detail", event_id=event_id)

    if request.method == "POST":
        form = EventCreationForm(request.POST, instance=event)
        if form.is_valid():
            updated_event = form.save(commit=False)

            # Update the associated post
            if event.post:
                event.post.title = form.cleaned_data["title"]
                event.post.body = form.cleaned_data["details"]
                event.post.save()

            # Save the event
            updated_event.save()

            messages.success(request, "Event updated successfully!")
            return redirect("event_detail", event_id=event_id)
    else:
        form = EventCreationForm(instance=event)

    return render(
        request,
        "events/edit.jinja",
        {"form": form, "event": event, "community": event.community},
    )

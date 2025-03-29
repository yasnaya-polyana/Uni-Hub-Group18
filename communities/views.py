import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import CustomUser
from events.forms import EventCreationForm
from events.models import Event
from notifications.manager import NotificationManager
from posts.forms import PostCreationForm
from posts.models import Post
from search.service import (
    compile_query,
    handle_search,
    search_communities,
    search_posts,
)

from .forms import CreateCommunityForm, EditCommunityForm
from .models import Communities, CommunityMember


@login_required
def community_create(request):
    if request.method == "POST":
        form = CreateCommunityForm(request.POST, user=request.user)
        if form.is_valid():
            com = form.save(commit=False)
            com.status = "pending"
            com.save()

            # Send notification to superuser
            superuser = CustomUser.objects.filter(is_superuser=True).first()
            NotificationManager.send_community_request(superuser, com)

            messages.success(request, "Community created and is pending approval.")
            return redirect("/c")
    else:
        form = CreateCommunityForm(user=request.user)

    return render(request, "communities/create.jinja", {"form": form})


@login_required
def create_event(request, community_id: str):
    if request.method == "POST":
        community = get_object_or_404(Communities, id=community_id)

        form = EventCreationForm(request.POST)
        if form.is_valid():
            # print(form.body)
            # print(form.start_at)
            # print(form.end_at)
            # print(form.location)
            event_post = Post()
            event_post.community = community
            event_post.title = form.cleaned_data["title"]
            event_post.body = form.cleaned_data["body"]
            event_post.user = request.user
            event_post.save()

            event = Event()
            event.community = community
            event.start_at = form.cleaned_data["start_at"]
            event.end_at = form.cleaned_data["end_at"]
            event.location = form.cleaned_data["location"]
            event.post = event_post
            event.user = request.user
            event.save()

    else:
        form = EventCreationForm()

    return render(request, "events/create.jinja", {"form": form})


@login_required
def community_edit(request, community_id):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    if (
        not user.is_superuser
        and user != community.owner
        and not CommunityMember.objects.filter(
            user=user, community=community, role="moderator"
        ).exists()
    ):
        return HttpResponse(status=403)

    if request.method == "POST":
        form = EditCommunityForm(request.POST, request.FILES, instance=community)
        if form.is_valid():
            form.save()
            messages.success(request, "Community details updated successfully!")
            return redirect("community_detail", community_id=community_id)
    else:
        form = EditCommunityForm(instance=community)

    return render(
        request,
        "communities/community-edit.jinja",
        {"form": form, "community": community},
    )


@login_required
def community_list(request):
    search_query = request.GET.get("q", "")
    category = request.GET.get("category", "")
    size = request.GET.get("size", "")
    activity = request.GET.get("activity", "")
    created = request.GET.get("created", "")
    membership = request.GET.get("membership", "")
    sort = request.GET.get("sort", "newest")

    # Start with all communities
    all_communities = Communities.objects.all()

    # Apply search query
    if search_query:
        all_communities = all_communities.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Apply category filter
    if category:
        all_communities = all_communities.filter(category=category)

    # Apply size filter
    if size:
        if size == "small":
            all_communities = all_communities.annotate(
                member_count=Count("members")
            ).filter(member_count__lt=50)
        elif size == "medium":
            all_communities = all_communities.annotate(
                member_count=Count("members")
            ).filter(member_count__gte=50, member_count__lte=200)
        elif size == "large":
            all_communities = all_communities.annotate(
                member_count=Count("members")
            ).filter(member_count__gt=200)

    # Apply activity filter
    if activity:
        # This would need a way to measure activity, for example by counting recent posts
        import datetime

        from django.utils import timezone

        if activity == "very_active":
            one_week_ago = timezone.now() - datetime.timedelta(days=7)
            all_communities = all_communities.annotate(
                recent_post_count=Count(
                    "posts", filter=Q(posts__created_at__gte=one_week_ago)
                )
            ).filter(recent_post_count__gte=10)
        elif activity == "active":
            one_week_ago = timezone.now() - datetime.timedelta(days=7)
            all_communities = all_communities.annotate(
                recent_post_count=Count(
                    "posts", filter=Q(posts__created_at__gte=one_week_ago)
                )
            ).filter(recent_post_count__gte=5, recent_post_count__lt=10)
        elif activity == "somewhat_active":
            one_week_ago = timezone.now() - datetime.timedelta(days=7)
            all_communities = all_communities.annotate(
                recent_post_count=Count(
                    "posts", filter=Q(posts__created_at__gte=one_week_ago)
                )
            ).filter(recent_post_count__gte=1, recent_post_count__lt=5)
        elif activity == "inactive":
            one_week_ago = timezone.now() - datetime.timedelta(days=7)
            all_communities = all_communities.annotate(
                recent_post_count=Count(
                    "posts", filter=Q(posts__created_at__gte=one_week_ago)
                )
            ).filter(recent_post_count=0)

    # Apply creation date filter
    if created:
        import datetime

        from django.utils import timezone

        if created == "last_week":
            one_week_ago = timezone.now() - datetime.timedelta(days=7)
            all_communities = all_communities.filter(created_at__gte=one_week_ago)
        elif created == "last_month":
            one_month_ago = timezone.now() - datetime.timedelta(days=30)
            all_communities = all_communities.filter(created_at__gte=one_month_ago)
        elif created == "last_3months":
            three_months_ago = timezone.now() - datetime.timedelta(days=90)
            all_communities = all_communities.filter(created_at__gte=three_months_ago)
        elif created == "last_year":
            one_year_ago = timezone.now() - datetime.timedelta(days=365)
            all_communities = all_communities.filter(created_at__gte=one_year_ago)

    # Apply membership filter (if user is authenticated)
    if request.user.is_authenticated and membership:
        if membership == "member":
            all_communities = all_communities.filter(members=request.user)
        elif membership == "not_member":
            all_communities = all_communities.exclude(members=request.user)
        elif membership == "owner":
            all_communities = all_communities.filter(owner=request.user)
        elif membership == "moderator":
            all_communities = all_communities.filter(
                communitymembership__user=request.user,
                communitymembership__role="moderator",
            )

    # Apply sorting
    if sort == "name_asc":
        all_communities = all_communities.order_by("name")
    elif sort == "name_desc":
        all_communities = all_communities.order_by("-name")
    elif sort == "newest":
        all_communities = all_communities.order_by("-created_at")
    elif sort == "oldest":
        all_communities = all_communities.order_by("created_at")
    elif sort == "most_members":
        all_communities = all_communities.annotate(
            member_count=Count("members")
        ).order_by("-member_count")
    elif sort == "most_posts":
        all_communities = all_communities.annotate(post_count=Count("posts")).order_by(
            "-post_count"
        )
    elif sort == "most_active":
        import datetime

        from django.utils import timezone

        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        all_communities = all_communities.annotate(
            recent_post_count=Count(
                "posts", filter=Q(posts__created_at__gte=one_week_ago)
            )
        ).order_by("-recent_post_count")

    # Get user's communities if authenticated
    user_communities = []
    if request.user.is_authenticated:
        user_communities = Communities.objects.filter(owner=request.user)

    return render(
        request,
        "communities/community-list.jinja",
        {
            "all_communities": all_communities,
            "user_communities": user_communities,
            "search_str": search_query,
        },
    )


@login_required
def community_detail(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    is_owner = request.user == community.owner

    is_moderator = CommunityMember.objects.filter(
        user=request.user, community=community, role="moderator"
    ).exists()

    is_member = CommunityMember.objects.filter(
        user=request.user, community=community, role="member"
    ).exists()

    if request.method == "POST":
        form = PostCreationForm(request.POST)
        if form.is_valid() and (is_owner or is_moderator or is_member):
            post = form.save(commit=False)
            post.user = request.user
            post.community = community
            post.save()
            return redirect("community_detail", community_id=community_id)
    else:
        form = PostCreationForm()

    membership = CommunityMember.objects.filter(
        user=request.user,
        community=community,
    ).first()

    events = community.events.filter(end_at__gte=datetime.date.today())

    posts = community.posts
    query_str = request.GET.get("q", "")
    query = compile_query(query_str)
    posts = search_posts(posts, query)
    context = {
        "community": community,
        "membership": membership,
        "events": events,
        "posts": posts,
        "search_str": query_str,
        "owner_username": community.owner.username,
        "is_owner": is_owner,
        "is_moderator": is_moderator,
        "is_member": is_member,
        "form": form,
    }
    return render(request, "communities/page.jinja", context)


@login_required
def community_join(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    is_already_member = (
        CommunityMember.objects.filter(user=user, community=community).count() > 0
    )

    if is_already_member:
        messages.warning(request, "You are already a member of this community.")
        return HttpResponse(status=204)

    CommunityMember.objects.create(user=user, community=community)
    messages.success(request, f"You have joined {community.name}!")
    #############################################################
    ########### Old Soft Delete Code removed for feed ###########
    #############################################################
    # membership = CommunityMember.all_objects.filter(
    #     user=user, community=community
    # ).first()
    #
    # if membership:
    #     if membership.deleted_at:
    #         membership.restore()  # Restore the soft deleted record
    #         messages.success(request, f"Welcome back to {community.name}!")
    #     else:
    #         messages.warning(request, "You are already a member of this community.")
    # else:
    #     CommunityMember.objects.create(user=user, community=community)
    #     messages.success(request, f"You have joined {community.name}!")

    return redirect("community_detail", community_id=community_id)


@login_required
def community_delete(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    if not user.is_superuser and user != community.owner:
        return HttpResponse(status=403)

    community.delete()
    messages.success(request, f"Community '{community.name}' has been deleted.")

    return redirect("community_list")


@login_required
def request_role(request, community_id: str, role: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    membership = CommunityMember.objects.filter(user=user, community=community).first()
    if membership and membership.role == "subscriber" and role == "member":
        membership.role = "pending_member"
        membership.save()
        NotificationManager.send_role_request(community.owner, community, user, role)
        messages.success(
            request, f"You have requested to become a {role} of {community.name}."
        )
    elif membership and membership.role == "member" and role == "moderator":
        membership.role = "pending_moderator"
        membership.save()
        NotificationManager.send_role_request(community.owner, community, user, role)
        messages.success(
            request, f"You have requested to become a {role} of {community.name}."
        )
    else:
        messages.error(request, "You are not eligible to request this role.")

    return redirect("community_detail", community_id=community_id)


@login_required
def community_restore(request, community_id: str):
    community = get_object_or_404(Communities.all_objects, id=community_id)
    user = request.user

    if not user.is_superuser:
        return HttpResponse(status=403)

    community.restore()

    return redirect("community_list")


@login_required
def community_leave(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    membership = CommunityMember.objects.filter(user=user, community=community).first()

    membership.delete()
    messages.success(request, f"You have left {community.name}.")

    #############################################################
    ########### Old Soft Delete Code removed for feed ###########
    #############################################################
    # membership = CommunityMember.all_objects.filter(
    #     user=user, community=community
    # ).first()

    # if membership:
    #     if membership.deleted_at:
    #         messages.warning(request, "You have already left this community.")
    #     else:
    #         membership.delete()  # Soft delete instead of hard delete
    #         messages.success(request, f"You have left {community.name}.")
    # else:
    #     messages.warning(request, "You are not a member of this community.")

    return redirect("community_detail", community_id=community_id)

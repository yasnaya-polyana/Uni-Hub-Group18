import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from search.service import (
    compile_query,
    handle_search,
    search_communities,
    search_posts,
)

from .forms import CreateCommunityForm
from .models import Communities, CommunityMember


@login_required
def community_create(request):
    if request.method == "POST":
        form = CreateCommunityForm(request.POST, user=request.user)
        if form.is_valid():

            com = form.save(commit=False)
            print(com.id)

            check_community = Communities.all_objects.filter(id=com.id).count()
            if check_community > 0:
                return render(
                    request, "communities/restore.jinja", {"community_id": com.id}
                )

            com.save()
            return redirect("/c")
    else:
        form = CreateCommunityForm(user=request.user)

    return render(request, "communities/create.jinja", {"form": form})


@login_required
def community_list(request):
    # filter these later???
    qs = Communities.objects

    query_str = request.GET.get("q", "")
    query = compile_query(query_str)
    communities = search_communities(qs, query)

    print(query_str)

    return render(
        request,
        "communities/community-list.jinja",
        {"communities": communities, "search_str": query_str},
    )


@login_required
def community_detail(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)

    # get active memberships
    membership = CommunityMember.objects.filter(
        user=request.user,
        community=community,
        # deleted_at__isnull=True
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

    if not user.is_superuser:
        return HttpResponse(status=403)

    community.delete()

    return redirect("community_list")


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

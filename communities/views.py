from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CreateCommunityForm, EditCommunityForm
from .models import Communities, CommunityMember
from posts.forms import PostCreationForm
from notifications.manager import NotificationManager
from accounts.models import CustomUser

@login_required
def community_create(request):
    if request.method == "POST":
        form = CreateCommunityForm(request.POST, user=request.user)
        if form.is_valid():
            com = form.save(commit=False)
            com.status = 'pending'
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
def approve_community(request, community_id: str):
    if not request.user.is_superuser:
        return HttpResponse(status=403)
    
    community = get_object_or_404(Communities, id=community_id)
    community.status = 'approved'
    community.save()
    messages.success(request, f"Community '{community.name}' has been approved.")
    return redirect("community_list")

@login_required
def reject_community(request, community_id: str):
    if not request.user.is_superuser:
        return HttpResponse(status=403)
    
    community = get_object_or_404(Communities, id=community_id)
    community.status = 'rejected'
    community.save()
    messages.success(request, f"Community '{community.name}' has been rejected.")
    return redirect("community_list")

@login_required
def community_edit(request, community_id):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    if not user.is_superuser and user != community.owner and not CommunityMember.objects.filter(user=user, community=community, role="moderator").exists():
        return HttpResponse(status=403)

    if request.method == "POST":
        form = EditCommunityForm(request.POST, request.FILES, instance=community)
        if form.is_valid():
            form.save()
            messages.success(request, "Community details updated successfully!")
            return redirect("community_detail", community_id=community_id)
    else:
        form = EditCommunityForm(instance=community)
    
    return render(request, "communities/community-edit.jinja", {"form": form, "community": community})

@login_required
def community_list(request):
    all_communities = Communities.objects.filter(status='approved')
    user_communities = Communities.objects.filter(owner=request.user, status='approved')

    return render(
        request,
        "communities/community-list.jinja",
        {"all_communities": all_communities, "user_communities": user_communities},
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

    context = {
        "community": community,
        "membership": membership,
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
def request_member(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    membership = CommunityMember.objects.filter(user=user, community=community).first()
    if membership and membership.role == "subscriber":
        membership.role = "member"
        membership.save()
        messages.success(request, f"You have requested to become a member of {community.name}.")
    else:
        messages.error(request, "You are not eligible to request member status.")

    return redirect("community_detail", community_id=community_id)

@login_required
def request_mod(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    membership = CommunityMember.objects.filter(user=user, community=community).first()
    if membership and membership.role == "member":
        membership.role = "moderator"
        membership.save()
        messages.success(request, f"You have requested to become a moderator of {community.name}.")
    else:
        messages.error(request, "You are not eligible to request moderator status.")

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

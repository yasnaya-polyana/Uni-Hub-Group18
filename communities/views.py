from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateCommunityForm
from .models import Communities, CommunityMember
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def community_create(request):
    if request.method == 'POST':
        form = CreateCommunityForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('some_success_url')
    else:
        form = CreateCommunityForm(user=request.user)

    return render(request, 'communities/community_create.html', {'form': form})

@login_required
def community_list(request):
    #filter these later???
    communities = Communities.objects.all()

    return render(request, 'communities/community_list.html', {'communities': communities})

@login_required
def community_detail(request, community_id):
    community = get_object_or_404(Communities, pk=community_id)

    # get active memberships
    membership = CommunityMember.objects.filter(
        user=request.user,
        community=community,
        deleted_at__isnull=True
    ).first()

    context = {
        "community": community,
        "membership": membership,
    }

    return render(request, "communities/community_detail.html", context)

@login_required
def community_join(request, community_id):
    community = get_object_or_404(Communities, pk=community_id)
    user = request.user

    membership = CommunityMember.all_objects.filter(user=user, community=community).first()

    if membership:
        if membership.deleted_at:
            membership.restore()  # Restore the soft deleted record
            messages.success(request, f"Welcome back to {community.name}!")
        else:
            messages.warning(request, "You are already a member of this community.")
    else:
        CommunityMember.objects.create(user=user, community=community)
        messages.success(request, f"You have joined {community.name}!")

    return redirect("community_detail", community_id=community_id)

@login_required
def community_leave(request, community_id):
    community = get_object_or_404(Communities, pk=community_id)
    user = request.user

    membership = CommunityMember.all_objects.filter(user=user, community=community).first()

    if membership:
        if membership.deleted_at:
            messages.warning(request, "You have already left this community.")
        else:
            membership.delete()  # Soft delete instead of hard delete
            messages.success(request, f"You have left {community.name}.")
    else:
        messages.warning(request, "You are not a member of this community.")

    return redirect("community_detail", community_id=community_id)

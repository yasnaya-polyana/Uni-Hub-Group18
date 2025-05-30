import datetime
import json

from accounts.models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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
from .models import Communities, CommunityMember, Topic


@login_required
def community_create(request):
    if request.method == "POST":
        form = CreateCommunityForm(request.POST)
        print("--- POST Request Received ---")
        print(f"Form is bound: {form.is_bound}")
        print(f"Is form valid? {form.is_valid()}")

        if form.is_valid():
            print("Form is valid. Attempting to save...")
            try:
                community = form.save(commit=False)
                community.owner = request.user
                community.category = form.cleaned_data.get("category", "society")

                # Auto-approve if admin is creating the community
                if request.user.is_superuser:
                    community.status = "approved"
                    success_message = (
                        f"Community '{community.name}' has been created successfully."
                    )
                else:
                    community.status = "pending"  # Set status to pending for approval
                    success_message = f"Community '{community.name}' has been submitted for approval. You will be notified once it's approved."

                community.save()

                # Save ManyToMany fields if they exist
                if "topics" in form.cleaned_data:
                    community.topics.set(form.cleaned_data["topics"])

                # Only send notifications if the community is pending
                if community.status == "pending":
                    # Send notifications to all admin users
                    admin_users = CustomUser.objects.filter(is_superuser=True)
                    for admin in admin_users:
                        NotificationManager.send_community_request(
                            superuser=admin, community=community
                        )

                print(f"Community saved with ID: {community.id}")
                messages.success(request, success_message)
                return redirect("community_list")
            except Exception as e:
                print(f"ERROR during save/redirect: {e}")
                messages.error(
                    request, f"An error occurred while saving the community: {e}"
                )
                context = {"form": form, "save_error": str(e)}
                return render(request, "communities/create.jinja", context)

        else:
            print("Form is NOT valid.")
            print(f"Form errors: {form.errors.as_json()}")
            messages.error(request, "Please correct the errors below.")

    else:  # GET request
        form = CreateCommunityForm()
        print("--- GET Request Received ---")

    context = {"form": form}
    return render(request, "communities/create.jinja", context)


@login_required
def community_edit(request, community_id):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    # Check permissions
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
            print("Invalid form.")
            print(form.errors)  # Debugging: Print field-specific errors
            print(form.non_field_errors())  # Debugging: Print non-field errors
    else:
        form = EditCommunityForm(instance=community)

    return render(
        request,
        "communities/community-edit.jinja",
        {"form": form, "community": community},
    )


@login_required
def community_list(request):
    query_str = request.GET.get("q", "")
    selected_category = request.GET.get("category", "")  # Get selected category
    selected_topics = request.GET.getlist("topic")  # Get list of selected topic IDs

    # --- Add Debug Prints ---
    print(f"--- Request GET: {request.GET}")
    print(f"Selected Category: '{selected_category}' (Type: {type(selected_category)})")
    print(f"Selected Topics: {selected_topics} (Type: {type(selected_topics)})")
    # -----------------------

    query = compile_query(query_str)

    # Your created communities (include pending communities for the owner)
    created_communities = Communities.objects.filter(
        owner=request.user, status="approved"
    )

    # Your followed communities (only approved ones)
    followed_communities = Communities.objects.filter(
        members=request.user, status="approved"
    ).exclude(owner=request.user)

    # Pending communities that need approval (only for admins)
    pending_communities = []
    if request.user.is_superuser:
        pending_communities = Communities.objects.filter(status="pending")

    # --- Filter all_communities (only approved ones) ---
    all_communities = Communities.objects.filter(status="approved")

    # Apply category filter if selected
    if selected_category:
        all_communities = all_communities.filter(category=selected_category)

    # Apply topic filter if selected
    # Ensure selected_topics contains valid IDs if necessary
    if selected_topics:
        # Filter communities that have AT LEAST ONE of the selected topics
        all_communities = all_communities.filter(
            topics__id__in=selected_topics
        ).distinct()
        # If you want communities that have ALL selected topics, you'd need a loop or different approach.

    # Apply text search to the already filtered list
    all_communities = search_communities(all_communities, query)
    # -----------------------------

    # Get all available topics for the filter dropdown/checkboxes
    available_topics = Topic.objects.all()  # Assuming you have a Topic model imported

    # --- Add Debug Print Before Render ---
    print(f"Final 'all_communities' count: {all_communities.count()}")
    # ------------------------------------

    return render(
        request,
        "communities/community-list.jinja",
        {
            "created_communities": created_communities,
            "followed_communities": followed_communities,
            "all_communities": all_communities,
            "pending_communities": pending_communities,
            "search_str": query_str,
            # Pass filter values back to template to keep them selected
            "selected_category": selected_category,
            "selected_topics": selected_topics,  # Pass list of IDs
            "available_topics": available_topics,  # For rendering filter options
            "category_choices": Communities.CATEGORY_CHOICES,  # Pass choices for category dropdown
            "is_admin": request.user.is_superuser,  # For admin UI elements
        },
    )


@login_required
def community_detail(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    is_owner = request.user == community.owner
    is_admin = request.user.is_superuser
    
    # Trying to get Topics
    topics = Topic.objects.filter(communities__id=community_id)
    
    print(topics)

    # Check if the community is pending and restrict access to owner and admins
    if community.status == "pending" and not (is_owner or is_admin):
        messages.error(
            request,
            "This community is awaiting approval and is not publicly accessible yet.",
        )
        return redirect("community_list")

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
            
            # Add selected topics as hashtags to post body - only add once
            if 'topics' in form.cleaned_data and form.cleaned_data['topics']:
                selected_topics = form.cleaned_data['topics']
                topic_tags = []
                
                # Create a list of hashtags for the selected topics
                for topic in selected_topics:
                    topic_tags.append(f"#{topic.name}")
                
                # Add the hashtags to the post body if they're not already included
                if post.body and topic_tags:
                    # Only append if not already in text
                    existing_text = post.body.strip()
                    hashtag_text = " ".join(topic_tags)
                    
                    # Check if the hashtags are already in the post
                    if not any(tag.lower() in existing_text.lower() for tag in topic_tags):
                        # Add a newline if the post doesn't end with one
                        if existing_text and not existing_text.endswith("\n"):
                            post.body = existing_text + "\n\n" + hashtag_text
                        else:
                            post.body = existing_text + hashtag_text
            
            # Handle visibility setting
            visibility = request.POST.get('visibility', 'public')
            # Only allow moderators and owners to set moderator-only visibility
            if visibility == 'moderators' and not (is_moderator or is_owner or is_admin):
                visibility = 'public'
            post.visibility = visibility
            
            post.save()
            
            # Save m2m relationships
            form.save_m2m()
            
            # Process hashtags from body - use the topics already associated with the post
            # Don't add existing topics from hashtags since they're already included
            return redirect("community_detail", community_id=community_id)
    else:
        form = PostCreationForm()

    # Debug the form output
    print("Form topics field type:", type(form.fields['topics']))
    print("Form topics widget type:", type(form.fields['topics'].widget))
    
    membership = CommunityMember.objects.filter(
        user=request.user,
        community=community,
    ).first()

    if membership and membership.is_suspended and not (is_owner or is_admin):
        messages.error(request, "You have been suspended from this community and cannot view its content.")
        return redirect("community_list")

    # Check if the community is pending and restrict access to owner and admins
    if community.status == 'pending' and not (is_owner or is_admin):
        messages.error(request, "This community is awaiting approval and is not publicly accessible yet.")
        return redirect("community_list")
    
    # Start with all posts in this community
    posts = community.posts
    
    # Filter posts based on user role and post visibility
    if not (is_owner or is_admin):
        # Get list of suspended users
        suspended_users = CommunityMember.objects.filter(
            community=community,
            is_suspended=True
        ).values_list('user', flat=True)
        
        # Exclude posts from suspended users
        posts = posts.exclude(user__in=suspended_users)
        
        # Filter posts by visibility
        if is_moderator:
            # Moderators can see public, members-only and moderators-only posts
            pass  # No additional filtering needed
        elif is_member:
            # Members can see public and members-only posts
            posts = posts.exclude(visibility='moderators')
        else:
            # Non-members can only see public posts
            posts = posts.filter(visibility='public')

    # Rest of your code
    events = community.events.filter(end_at__gte=datetime.date.today())

    query_str = request.GET.get("q", "")
    query = compile_query(query_str)
    posts = search_posts(posts, query).order_by("created_at").order_by("-is_pinned")
    
    context = {
        "community": community,
        "topics": topics,
        "membership": membership,
        "events": events,
        "posts": posts,
        "search_str": query_str,
        "owner_username": community.owner.username,
        "is_owner": is_owner,
        "is_moderator": is_moderator,
        "is_member": is_member,
        "is_admin": is_admin,
        "is_pending": community.status == "pending",
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

    # Get the community name before deletion for the success message
    community_name = community.name

    # Delete all events associated with this community
    # This should happen automatically due to CASCADE, but we'll do it explicitly to be sure
    from events.models import Event

    Event.objects.filter(community=community).delete()

    # Now delete the community
    community.delete()
    messages.success(request, f"Community '{community_name}' has been deleted.")

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


@login_required
def community_invite(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user

    # Ensure user has permission to invite (owner or moderator)
    is_owner = user == community.owner
    is_moderator = CommunityMember.objects.filter(
        user=user, community=community, role="moderator"
    ).exists()

    if not (is_owner or is_moderator):
        messages.error(
            request, "You don't have permission to invite users to this community."
        )
        return redirect("community_detail", community_id=community_id)

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("community_detail", community_id=community_id)

    try:
        # Get username from form data instead of JSON
        username = request.POST.get("username")

        if not username:
            messages.error(request, "Please enter a username.")
            return redirect("community_detail", community_id=community_id)

        # Check if user exists
        try:
            invited_user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, f"User '{username}' not found.")
            return redirect("community_detail", community_id=community_id)

        # Don't invite self
        if invited_user == user:
            messages.error(request, "You cannot invite yourself.")
            return redirect("community_detail", community_id=community_id)

        # Check if user is already a member
        if CommunityMember.objects.filter(
            user=invited_user, community=community
        ).exists():
            messages.warning(
                request,
                f"{invited_user.username} is already a member of this community.",
            )
            return redirect("community_detail", community_id=community_id)

        # Send notification
        NotificationManager.send_community_invite(
            invited_user=invited_user, community=community, inviter=user
        )

        messages.success(request, f"Invitation sent to {invited_user.username}.")
        return redirect("community_detail", community_id=community_id)

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("community_detail", community_id=community_id)


@login_required
def create_event(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)

    # Check if user has permission to create events (must be a moderator or owner)
    is_moderator = CommunityMember.objects.filter(
        user=request.user, community=community, role="moderator"
    ).exists()
    is_owner = request.user == community.owner

    # Only allow moderators and the community owner to create events
    if not (is_moderator or is_owner):
        messages.error(
            request, "Only moderators and community owners can create events."
        )
        return redirect(f"/c/{community_id}")

    if request.method == "POST":
        form = EventCreationForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.community = community

            # Create a post for the event
            post = Post(
                title=form.cleaned_data["title"],
                body=form.cleaned_data["details"],
                user=request.user,
                community=community,
            )
            post.save()

            event.post = post
            event.user = request.user

            # Handle the members_only field if it exists
            members_only = request.POST.get('members_only') == 'on'

            event.members_only = members_only

            event.save()

            messages.success(request, "Event created successfully!")
            return redirect(f"/c/{community_id}")
    else:
        form = EventCreationForm()
    
    return render(request, "events/create.jinja", {"form": form, "community": community})

@login_required
def community_members(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user
    
    # Check permissions
    is_owner = user == community.owner
    is_admin = user.is_superuser
    is_moderator = CommunityMember.objects.filter(
        user=user, community=community, role="moderator"
    ).exists()
    
    # If not a member, owner, moderator or admin, redirect
    if not (is_owner or is_admin or is_moderator or CommunityMember.objects.filter(
        user=user, community=community
    ).exists()):
        messages.error(request, "You don't have permission to view community members.")
        return redirect("community_detail", community_id=community_id)
    
    # Get all members
    members = CommunityMember.objects.filter(community=community).select_related('user').order_by('role', 'user__username')
    
    return render(request, "communities/members.jinja", {
        "community": community,
        "members": members,
        "is_owner": is_owner,
        "is_admin": is_admin,
        "is_moderator": is_moderator,
    })

@login_required
def community_suspend_user(request, community_id: str, username: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user
    target_user = get_object_or_404(CustomUser, username=username)
    
    # Check if requester has permission to suspend (owner, moderator, admin)
    is_owner = user == community.owner
    is_moderator = CommunityMember.objects.filter(
        user=user, community=community, role="moderator"
    ).exists()
    is_admin = user.is_superuser
    
    if not (is_owner or is_moderator or is_admin):
        messages.error(request, "You don't have permission to suspend users from this community.")
        return redirect("community_detail", community_id=community_id)
    
    # Owner and admin can't be suspended
    if target_user == community.owner or target_user.is_superuser:
        messages.error(request, "Community owners and administrators cannot be suspended.")
        return redirect("community_detail", community_id=community_id)
    
    # Moderators can only be suspended by owners or admins
    target_membership = get_object_or_404(CommunityMember, user=target_user, community=community)
    if target_membership.role == "moderator" and not (is_owner or is_admin):
        messages.error(request, "Only community owners and administrators can suspend moderators.")
        return redirect("community_detail", community_id=community_id)
    
    # Set suspension status
    target_membership.is_suspended = True
    target_membership.save()
    
    messages.success(request, f"User '{username}' has been suspended from this community.")
    return redirect("community_detail", community_id=community_id)

@login_required
def community_unsuspend_user(request, community_id: str, username: str):
    community = get_object_or_404(Communities, id=community_id)
    user = request.user
    target_user = get_object_or_404(CustomUser, username=username)
    
    # Check if requester has permission
    is_owner = user == community.owner
    is_moderator = CommunityMember.objects.filter(
        user=user, community=community, role="moderator"
    ).exists()
    is_admin = user.is_superuser
    
    if not (is_owner or is_moderator or is_admin):
        messages.error(request, "You don't have permission to unsuspend users in this community.")
        return redirect("community_detail", community_id=community_id)
    
    # Unsuspend the user
    target_membership = get_object_or_404(CommunityMember, user=target_user, community=community)
    target_membership.is_suspended = False
    target_membership.save()
    
    messages.success(request, f"User '{username}' has been unsuspended from this community.")
    return redirect("community_detail", community_id=community_id)

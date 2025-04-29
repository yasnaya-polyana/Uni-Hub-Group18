from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView

from events.models import Event
from notifications.manager import NotificationManager
from posts.models import Post
from search.service import compile_query, search_accounts

from .decorators import anonymous_required
from .forms import (
    CustomLoginForm,
    CustomUserCreationForm,
    ProfileEditForm,
    UserSettingsForm,
)
from .models import CustomUser, Follow, UserFollow, UserSettings

# Create your views here.


def HomeView(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "home.jinja")


def user_search_view(request):
    search_query = request.GET.get("q", "")
    user_type = request.GET.get("user_type", "")
    department = request.GET.get("department", "")
    year = request.GET.get("year", "")
    activity = request.GET.get("activity", "")
    sort = request.GET.get("sort", "newest")

    # Start with all users
    users = CustomUser.objects.all()

    # Apply search query
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(bio__icontains=search_query)
        )

    # Apply user type filter
    if user_type:
        users = users.filter(user_type=user_type)

    # Apply department/major filter
    if department:
        users = users.filter(department__icontains=department)

    # Apply year filter
    if year:
        users = users.filter(year=year)

    # Apply activity filter (this would need a way to measure activity)
    if activity:
        if activity == "very_active":
            users = users.annotate(post_count=Count("posts")).filter(post_count__gte=20)
        elif activity == "active":
            users = users.annotate(post_count=Count("posts")).filter(
                post_count__gte=10, post_count__lt=20
            )
        elif activity == "somewhat_active":
            users = users.annotate(post_count=Count("posts")).filter(
                post_count__gte=5, post_count__lt=10
            )
        elif activity == "inactive":
            users = users.annotate(post_count=Count("posts")).filter(post_count__lt=5)

    # Apply sorting
    if sort == "name_asc":
        users = users.order_by("first_name", "last_name")
    elif sort == "name_desc":
        users = users.order_by("-first_name", "-last_name")
    elif sort == "newest":
        users = users.order_by("-date_joined")
    elif sort == "oldest":
        users = users.order_by("date_joined")
    elif sort == "most_posts":
        users = users.annotate(post_count=Count("posts")).order_by("-post_count")
    elif sort == "most_followers":
        users = users.annotate(follower_count=Count("followers")).order_by(
            "-follower_count"
        )

    return render(
        request,
        "accounts/user-search.jinja",
        {"users": users, "search_str": search_query},
    )


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.jinja", {"form": form})


@anonymous_required
def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
    else:
        form = CustomLoginForm()
    return render(request, "accounts/login.jinja", {"form": form})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "accounts/edit-profile.jinja", {"form": form})


@login_required
def user_settings_view(request):
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=user_settings)
        if form.is_valid():
            form.save()
            return redirect("user_settings")
    else:
        form = UserSettingsForm(instance=user_settings)
    return render(request, "accounts/user_settings.jinja", {"form": form})


# viewing your own profile
@login_required
def profile_view(request):
    profile_user = request.user
    return render(request, "accounts/profile.jinja", {"profile_user": profile_user})


# viewing different user profiles
@login_required
def user_profile_view(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    user_posts = Post.objects.filter(user=profile_user).order_by("-created_at")

    # Check if the current user is following this user
    is_following = False
    if request.user.is_authenticated:
        is_following = UserFollow.objects.filter(
            follower=request.user, followed=profile_user
        ).exists()

    context = {
        "profile_user": profile_user,
        "posts": user_posts,
        "is_following": is_following,
    }

    return render(request, "accounts/profile.jinja", context)


@login_required
def my_profile_view(request):
    return redirect("user", username=request.user.username)


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard_view(request):
    # Get posts from communities the user is a member of
    community_posts = Post.objects.filter(community__members=request.user)

    # Get posts from users the current user follows
    followed_users = request.user.user_following.values_list("followed", flat=True)
    followed_posts = Post.objects.filter(
        user__in=followed_users, community__isnull=True
    )

    # Get the current user's own posts
    user_posts = Post.objects.filter(user=request.user, community__isnull=True)

    # Combine and sort all posts
    posts = (community_posts | followed_posts | user_posts).order_by("-created_at")

    # Get only the user's posts for the "My Posts" section
    my_posts = Post.objects.filter(user=request.user).order_by("-created_at")

    events = Event.objects.filter(
        post__interactions__interaction="rsvp", post__interactions__user=request.user
    ).order_by("start_at")

    # event.post.interactions.filter(interaction="rsvp", user_id=user.id, post_id=event.post.pkid)
    return render(
        request,
        "dashboard/index.jinja",
        {"posts": posts, "my_posts": my_posts, "events": events},
    )


@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(CustomUser, username=username)

    # Don't allow users to follow themselves
    if request.user == user_to_follow:
        messages.error(request, "You cannot follow yourself.")
        return redirect("user", username=username)

    # Check if already following
    if UserFollow.objects.filter(
        follower=request.user, followed=user_to_follow
    ).exists():
        messages.info(request, f"You are already following {username}.")
    else:
        UserFollow.objects.create(follower=request.user, followed=user_to_follow)
        messages.success(request, f"You are now following {username}.")
        NotificationManager.send_follow(username, request.user.username)

    return redirect("user", username=username)


@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(CustomUser, username=username)

    follow = UserFollow.objects.filter(
        follower=request.user, followed=user_to_unfollow
    ).first()
    if follow:
        follow.delete()
        messages.success(request, f"You have unfollowed {username}.")
    else:
        messages.info(request, f"You were not following {username}.")

    return redirect("user", username=username)

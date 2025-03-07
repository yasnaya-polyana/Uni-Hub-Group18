"""
URL configuration for uni_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from accounts import views
from communities import views as community_views
from events import views as event_views
from posts import views as post_views

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Root
    path("", views.HomeView.as_view(), name="home"),
    # Dashboard
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # Auth
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    # Users
    path("u/<str:username>/", views.user_profile_view, name="user"),
    path("profile/", views.my_profile_view, name="my_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    # Posts
    path("p/", post_views.posts_view, name="posts"),
    path("p/create/", post_views.post_create, name="post_create"),
    path("p/<str:post_id>/", post_views.post_view, name="post"),
    path("p/<str:post_id>/comment", post_views.post_comment, name="post_comment"),
    path("p/<str:post_id>/repost", post_views.post_repost, name="post_repost"),
    path("p/<str:post_id>/pin", post_views.post_pin, name="post_pin"),
    path(
        "p/<str:post_id>/interact/<str:interaction>",
        post_views.post_interact,
        name="post_interact",
    ),
    # Communities
    path("c/", community_views.community_list, name="community_list"),
    path("c/create", community_views.community_create, name="community_create"),
    path(
        "c/<str:community_id>/",
        community_views.community_detail,
        name="community_detail",
    ),
    path(
        "c/<str:community_id>/join",
        community_views.community_join,
        name="community_join",
    ),
    path(
        "c/<str:community_id>/leave",
        community_views.community_leave,
        name="community_leave",
    ),
    path(
        "c/<str:community_id>/delete",
        community_views.community_delete,
        name="community_delete",
    ),
    path(
        "c/<str:community_id>/restore",
        community_views.community_restore,
        name="community_restore",
    ),
    # Events
    path("events/", event_views.events_list, name="events"),
    # Password Reset
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.jinja",
            subject_template_name="registration/password_reset_subject.txt",
            email_template_name="registration/password_reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.jinja"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.jinja"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.jinja"
        ),
        name="password_reset_complete",
    ),
    # API
    path("api/", include("api.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

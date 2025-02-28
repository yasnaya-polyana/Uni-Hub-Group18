from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from .decorators import anonymous_required
from .forms import CustomLoginForm, CustomUserCreationForm, ProfileEditForm

# Create your views here.


class HomeView(TemplateView):
    template_name = "home.jinja"


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
def profile_view(request):
    return render(request, "accounts/profile.jinja")


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard_view(request):
    return render(request, "dashboard/index.jinja")

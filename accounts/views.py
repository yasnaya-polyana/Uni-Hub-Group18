from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from .forms import CustomUserCreationForm, CustomLoginForm, ProfileEditForm
from .models import CustomUser, Follow
from .decorators import anonymous_required

# Create your views here.

class HomeView(TemplateView):
    template_name = 'home.html'

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@anonymous_required
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

#viewing your own profile
@login_required
def profile_view(request):
    profile_user = request.user
    return render(request, 'accounts/profile.html', {'profile_user': profile_user})

#viewing different user profiles
@login_required
def user_profile_view(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    is_following = Follow.objects.filter(follower=request.user, followee=profile_user).exists()

    if request.method == 'POST':
        if 'follow' in request.POST:
            Follow.objects.get_or_create(follower=request.user, followee=profile_user)
        elif 'unfollow' in request.POST:
            Follow.objects.filter(follower=request.user, followee=profile_user).delete()
        return redirect('user-profile', username=username)

    return render(request, 'accounts/profile.html', {'profile_user': profile_user, 'is_following': is_following})

def logout_view(request):
    logout(request)
    return redirect('home')
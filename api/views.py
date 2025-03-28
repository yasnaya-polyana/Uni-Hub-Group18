from rest_framework import generics
from communities.models import Communities
from accounts.models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET
from django.db.models import Q

class UserProfileDetail(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = get_object_or_404(CustomUser, username=self.kwargs['username'])
        return user
    
User = get_user_model()

@login_required
@require_GET
def community_search_api(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse([], safe=False)

    communities = Communities.objects.filter(
        Q(id__icontains=query) |
        Q(name__icontains=query)
    )[:10]  # Limit to 10 results

    results = [
        {
            "display_name": community.name,
            "id": community.id
        }
        for community in communities
    ]

    return JsonResponse(results, safe=False)

@login_required
@require_GET
def user_search_api(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse([], safe=False)

    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )[:10]  # Limit to 10 results

    results = [
        {
            "username": user.username,
            "display_name": user.get_full_name() or user.username,
            "avatar_url": user.profile.avatar_url if hasattr(user, 'profile') else "",  # optional
        }
        for user in users
    ]

    return JsonResponse(results, safe=False)
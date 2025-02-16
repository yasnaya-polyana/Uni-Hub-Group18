from rest_framework import generics
from accounts.models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

class UserProfileDetail(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = get_object_or_404(CustomUser, username=self.kwargs['username'])
        return user
from django.urls import path
from .views import UserProfileDetail

# Setup API End-points
#
urlpatterns = [
    path('profiles/<str:username>/', UserProfileDetail.as_view(), name='user-profile-detail'), # Detail by username
]
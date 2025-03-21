from django.urls import path
from .views import UserProfileDetail
from .views import user_search_api

# Setup API End-points
#
urlpatterns = [
    path('profiles/<str:username>/', UserProfileDetail.as_view(), name='user-profile-detail-api'),
    path('user-search/', user_search_api, name='user-search-api'),
]
from django.urls import path
from .views import UserProfileDetail
from .views import user_search_api
from .views import community_search_api

# Setup API End-points
#
urlpatterns = [
    path('profiles/<str:username>/', UserProfileDetail.as_view(), name='user-profile-detail-api'),

    # Post Search API
    path('user-search/', user_search_api, name='user-search-api'),
    path('community-search/', community_search_api, name='community-search-api'),
]
from django.urls import path

from . import views

urlpatterns = [
    path("", views.events_list, name="events"),
    path("<str:event_id>/", views.event_detail, name="event_detail"),
    path("<str:event_id>/edit/", views.event_edit, name="edit_event"),
] 
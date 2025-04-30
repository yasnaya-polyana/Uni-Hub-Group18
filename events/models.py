import datetime
from django.utils import timezone

import nanoid
from django.contrib import admin
from django.db import models

from accounts.models import CustomUser
from communities.models import Communities
from posts.models import Post


def generate_nanoid():
    return nanoid.generate()


class Event(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.CharField(default=generate_nanoid, editable=False, unique=True)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True, related_name="event"
    )  # TODO: Should probably be OneToOneField

    location = models.CharField(max_length=200)

    community = models.ForeignKey(
        Communities,
        on_delete=models.CASCADE,
        related_name="events",
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    title = models.CharField(max_length=100)
    details = models.TextField()
    
    # These fields are commented out but will be used in the code via hasattr
    # members_only = models.BooleanField(default=False)
    # materials = models.FileField(upload_to='event_materials/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_finished(self):
        """Checks if the event's end time has passed."""
        return timezone.now() > self.end_at

    @property
    def is_ongoing(self):
        """Checks if the event is currently happening."""
        now = timezone.now()
        return self.start_at <= now <= self.end_at
    
    @property
    def members_only(self):
        """Provides a fallback for the members_only field."""
        if hasattr(self, '_members_only'):
            return self._members_only
        return False
    
    @members_only.setter
    def members_only(self, value):
        """Setter for members_only that works even if the field doesn't exist."""
        self._members_only = value

    def is_past_due(self):
        cur_time = timezone.now()
        return self.start_at < cur_time

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["start_at"]


class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "start_at", "end_at", "post", "created_at")


admin.site.register(Event, EventAdmin)

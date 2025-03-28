import datetime

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

    location = models.CharField()

    community = models.ForeignKey(
        Communities,
        on_delete=models.CASCADE,
        related_name="events",
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def isOngoing(self):
        cur_time = datetime.datetime.now(datetime.UTC)
        return self.start_at < cur_time


class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "start_at", "end_at", "post", "created_at")


admin.site.register(Event, EventAdmin)

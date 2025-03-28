import nanoid
from django.contrib import admin
from django.db import models

from events.models import Event

from .models import Post


class EventInline(admin.TabularInline):
    model = Event


class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "parent_post", "created_at")
    inlines = (EventInline,)


admin.site.register(Post, PostAdmin)

import nanoid
from django.contrib import admin
from django.db import models

from accounts.models import CustomUser


def generate_nanoid():
    return nanoid.generate()


class Post(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.CharField(default=generate_nanoid, editable=False, unique=True)

    title = models.CharField(max_length=60)
    body = models.TextField(max_length=1000)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    parent_post = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="comments"
    )
    ref_post = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="reposts"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "parent_post", "created_at")


class Interaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="interactions"
    )
    interaction = models.CharField(max_length=20)


admin.site.register(Post, PostAdmin)
admin.site.register(Interaction)

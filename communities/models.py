from django.db import models

from accounts.models import CustomUser
from common.models import SoftDeleteModel


# Communities
class Communities(SoftDeleteModel):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.CharField(max_length=25, unique=True)

    owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="owned_communities"
    )

    members = models.ManyToManyField(
        CustomUser,
        through="CommunityMember",
        related_name="communities",
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    banner_url = models.URLField(blank=True, null=True)
    icon_url = models.URLField(blank=True, null=True)

    topics = models.ManyToManyField("Topic", blank=True, related_name="communities")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def members_count(self):
        return self.community_members.filter(
            # deleted_at__isnull=True
        ).count()

    def __str__(self):
        return self.name


# Community Member (Soft Delete Disabled)
class CommunityMember(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    community = models.ForeignKey(
        Communities, on_delete=models.CASCADE, related_name="community_members"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    COMMUNITY_ROLES = [
        ("subscriber", "Subscriber"),
        ("member", "Member"),
        ("moderator", "Moderator"),
    ]
    role = models.CharField(max_length=20, choices=COMMUNITY_ROLES, default="subscriber")

    class Meta:
        unique_together = ("user", "community")

    def __str__(self):
        return f"{self.user.username} in {self.community.name} ({self.role})"


# Topics
class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


from django.contrib import admin

admin.site.register(Communities)
admin.site.register(Topic)
admin.site.register(CommunityMember)

from django.db import models
import nanoid

from accounts.models import CustomUser
from common.models import SoftDeleteModel


def generate_nanoid():
    return nanoid.generate()


# Communities
class Communities(SoftDeleteModel):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.CharField(default=generate_nanoid, unique=True, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500)
    owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="owned_communities"
    )
    members = models.ManyToManyField(
        CustomUser,
        through="CommunityMember",
        related_name="communities",
    )
    
    banner_url = models.ImageField(upload_to="banners/", null=True, blank=True)
    icon_url = models.ImageField(upload_to="icons/", null=True, blank=True)
    
    topics = models.ManyToManyField("Topic", blank=True, related_name="communities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    CATEGORY_CHOICES = [
        ('sports', 'Sports'),
        ('academic', 'Academic'),
        ('hobby', 'Hobby'),
        ('society', 'Society'),
    ]
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='society'
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def members_count(self):
        return self.community_members.filter(
            # deleted_at__isnull=True
        ).count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Communities"


# Community Member (Soft Delete Disabled)
class CommunityMember(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    community = models.ForeignKey(
        Communities, on_delete=models.CASCADE, related_name="community_members"
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    is_suspended = models.BooleanField(default=False)

    COMMUNITY_ROLES = [
        ("subscriber", "Subscriber"),
        ("member", "Member"),
        ("moderator", "Moderator"),
    ]
    role = models.CharField(max_length=20, choices=COMMUNITY_ROLES, default="subscriber")

    class Meta:
        unique_together = ("user", "community")

    def __str__(self):
        status = " (suspended)" if self.is_suspended else ""
        return f"{self.user.username} in {self.community.name} ({self.role})"


# Topics
class Topic(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


from django.contrib import admin

admin.site.register(Communities)
admin.site.register(Topic)
admin.site.register(CommunityMember)

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.conf import settings

# Create your models here.


# Course Types
#
#
class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.TextField(max_length=100)

    def __str__(self):
        return self.course_name


# Student Account Creation
#
#
class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    student_id = models.CharField(
        max_length=8,
        validators=[MinLengthValidator(8), MaxLengthValidator(8)],
        unique=True,
        null=True,
        blank=False,
    )
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.username

# User Settings Model
#
#
class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like_notifications = models.BooleanField(default=True)
    comment_notifications = models.BooleanField(default=True)
    follow_notifications = models.BooleanField(default=True)
    # Add other notification preferences as needed

    def __str__(self):
        return f"{self.user.username}'s Settings"

# Follow Model
#
#
class Follow(models.Model):
    follower = models.ForeignKey(
        CustomUser, related_name="following", on_delete=models.CASCADE
    )
    followee = models.ForeignKey(
        CustomUser, related_name="followers", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("follower", "followee")


# Update the UserFollow model with different related_name values
class UserFollow(models.Model):
    follower = models.ForeignKey(CustomUser, related_name='user_following', on_delete=models.CASCADE)
    followed = models.ForeignKey(CustomUser, related_name='user_followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')
        
    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"


from django.contrib import admin

admin.site.register(CustomUser)

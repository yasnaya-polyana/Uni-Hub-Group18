from django.db import models
from accounts.models import CustomUser

# Create your models here.
class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, default="default_type")
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type} - {self.username}"
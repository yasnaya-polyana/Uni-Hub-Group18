from django.db import models
from accounts.models import CustomUser
from communities.models import Communities
from events.models import Event

class UserInterest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='interests')
    category = models.CharField(max_length=50)
    weight = models.FloatField(default=1.0)  # How interested the user is in this category
    
    class Meta:
        unique_together = ('user', 'category')

class Recommendation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recommendations')
    community = models.ForeignKey(Communities, on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    score = models.FloatField()  # Relevance score
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = (('user', 'community'), ('user', 'event'))

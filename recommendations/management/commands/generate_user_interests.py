from django.core.management.base import BaseCommand
from django.db.models import Count
from accounts.models import CustomUser
from communities.models import Communities
from recommendations.models import UserInterest

class Command(BaseCommand):
    help = 'Generate user interests based on community memberships'

    def handle(self, *args, **options):
        self.stdout.write('Generating user interests...')
        
        # Clear existing interests
        UserInterest.objects.all().delete()
        
        # For each user
        for user in CustomUser.objects.all():
            # Get communities the user is a member of
            user_communities = Communities.objects.filter(members=user)
            
            # Count categories
            category_counts = {}
            for community in user_communities:
                category = community.category
                if category in category_counts:
                    category_counts[category] += 1
                else:
                    category_counts[category] = 1
            
            # Create interests
            for category, count in category_counts.items():
                # Weight is proportional to the number of communities in that category
                weight = min(5.0, count * 1.0)  # Cap at 5.0
                UserInterest.objects.create(
                    user=user,
                    category=category,
                    weight=weight
                )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated interests for {CustomUser.objects.count()} users')) 
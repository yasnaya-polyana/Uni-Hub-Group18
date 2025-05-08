from django.core.management.base import BaseCommand
from communities.models import Topic

class Command(BaseCommand):
    help = 'Initialize common topics for hashtags'

    def handle(self, *args, **options):
        # List of common topics to create
        TOPICS = [
            {"name": "Programming", "description": "Software development and coding topics"},
            {"name": "WebDev", "description": "Web development and design"},
            {"name": "DataScience", "description": "Data analysis, machine learning, and statistics"},
            {"name": "Gaming", "description": "Video games and esports"},
            {"name": "Music", "description": "Music creation, appreciation, and events"},
            {"name": "Sports", "description": "Athletic activities and sports news"},
            {"name": "Art", "description": "Visual arts, design, and creative expression"},
            {"name": "Science", "description": "Scientific research and discoveries"},
            {"name": "Math", "description": "Mathematics and related concepts"},
            {"name": "History", "description": "Historical events and perspectives"},
            {"name": "Literature", "description": "Books, poetry, and written works"},
            {"name": "Movies", "description": "Film and cinema discussion"},
            {"name": "Television", "description": "TV shows and streaming content"},
            {"name": "Food", "description": "Cooking, recipes, and culinary experiences"},
            {"name": "Travel", "description": "Travel experiences and destinations"},
            {"name": "Fashion", "description": "Clothing, style, and fashion trends"},
            {"name": "Technology", "description": "Tech news, gadgets, and innovations"},
            {"name": "Politics", "description": "Political discussions and current events"},
            {"name": "Health", "description": "Health and wellness topics"},
            {"name": "Fitness", "description": "Exercise, workouts, and physical fitness"},
            {"name": "UWE", "description": "University of the West of England related topics"},
            {"name": "CompSci", "description": "Computer Science topics"},
            {"name": "StudentLife", "description": "Student life experiences and discussions"}
        ]

        created_count = 0
        for topic_data in TOPICS:
            topic, created = Topic.objects.get_or_create(
                name=topic_data["name"],
                defaults={"description": topic_data["description"]}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created topic: {topic.name}"))

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} new topics")) 
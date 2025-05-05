#!/usr/bin/env python
"""
Script to initialize topics for hashtags
Run this script using:
docker exec -it django_container python initialize_topics.py
"""

import os
import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uni_hub.settings")
django.setup()

# Import the Topic model
from communities.models import Topic

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

# Create topics
created_count = 0
for topic_data in TOPICS:
    topic, created = Topic.objects.get_or_create(
        name=topic_data["name"],
        defaults={"description": topic_data["description"]}
    )
    if created:
        created_count += 1
        print(f"Created topic: {topic.name}")

print(f"Created {created_count} new topics") 
from django.core.management.base import BaseCommand
from accounts.models import Interest, Course

class Command(BaseCommand):
    help = 'Populates the database with common interests and university courses'

    def handle(self, *args, **kwargs):
        # Common interests
        interests = [
            # Academic Interests
            {"name": "Artificial Intelligence", "description": "Machine learning, neural networks, and AI applications"},
            {"name": "Robotics", "description": "Building and programming robots"},
            {"name": "Software Development", "description": "Programming and software engineering"},
            {"name": "Web Development", "description": "Creating websites and web applications"},
            {"name": "Data Science", "description": "Working with data and statistics"},
            {"name": "Cybersecurity", "description": "Computer and network security"},
            {"name": "Blockchain", "description": "Cryptocurrency and distributed ledger technology"},
            {"name": "Gaming", "description": "Video games and game development"},
            {"name": "Mobile Development", "description": "Creating mobile applications"},
            
            # Sports
            {"name": "Football", "description": "Association football/soccer"},
            {"name": "Basketball", "description": "Basketball and related activities"},
            {"name": "Tennis", "description": "Tennis and racket sports"},
            {"name": "Swimming", "description": "Swimming and water sports"},
            {"name": "Volleyball", "description": "Volleyball and related activities"},
            {"name": "Rugby", "description": "Rugby union and league"},
            {"name": "Athletics", "description": "Track and field activities"},
            {"name": "Cycling", "description": "Road and mountain biking"},
            {"name": "Fitness", "description": "Working out and physical fitness"},
            {"name": "Martial Arts", "description": "Various martial arts disciplines"},
            
            # Creative Arts
            {"name": "Photography", "description": "Taking and editing photos"},
            {"name": "Music", "description": "Playing instruments, singing, or producing music"},
            {"name": "Painting", "description": "Creating art through painting"},
            {"name": "Drawing", "description": "Sketching, illustration, and drawing"},
            {"name": "Writing", "description": "Creative writing, poetry, and storytelling"},
            {"name": "Film & Video", "description": "Filmmaking and video production"},
            {"name": "Dance", "description": "Various dance styles and choreography"},
            {"name": "Theater", "description": "Acting, directing, and theater production"},
            
            # Social Interests
            {"name": "Volunteering", "description": "Community service and helping others"},
            {"name": "Debate", "description": "Formal discussion and debate competitions"},
            {"name": "Cultural Exchange", "description": "Learning about different cultures"},
            {"name": "Entrepreneurship", "description": "Business startups and innovation"},
            {"name": "Environmental Activism", "description": "Conservation and ecological advocacy"},
        ]
        
        # University courses
        courses = [
            # Engineering
            {"course_name": "Computer Science", "department": "Engineering", "description": "Study of computational systems and programming"},
            {"course_name": "Software Engineering", "department": "Engineering", "description": "Applying engineering principles to software development"},
            {"course_name": "Electrical Engineering", "department": "Engineering", "description": "Study of electricity, electronics, and electromagnetism"},
            {"course_name": "Mechanical Engineering", "department": "Engineering", "description": "Design and analysis of mechanical systems"},
            {"course_name": "Civil Engineering", "department": "Engineering", "description": "Design and construction of physical infrastructure"},
            {"course_name": "Aerospace Engineering", "department": "Engineering", "description": "Design of aircraft, spacecraft, and related systems"},
            {"course_name": "Biomedical Engineering", "department": "Engineering", "description": "Application of engineering principles to medicine and biology"},
            
            # Business
            {"course_name": "Business Administration", "department": "Business", "description": "Management of business operations and organizations"},
            {"course_name": "Accounting", "department": "Business", "description": "Recording and analyzing financial transactions"},
            {"course_name": "Finance", "department": "Business", "description": "Management of money and assets"},
            {"course_name": "Marketing", "department": "Business", "description": "Promotion and selling of products or services"},
            {"course_name": "Economics", "department": "Business", "description": "Study of production, distribution, and consumption"},
            {"course_name": "International Business", "department": "Business", "description": "Business operations in international markets"},
            
            # Science
            {"course_name": "Physics", "department": "Science", "description": "Study of matter, energy, and the interactions between them"},
            {"course_name": "Chemistry", "department": "Science", "description": "Study of substances, their properties, and reactions"},
            {"course_name": "Biology", "department": "Science", "description": "Study of living organisms and their interactions"},
            {"course_name": "Environmental Science", "department": "Science", "description": "Study of environment and solutions to environmental problems"},
            {"course_name": "Mathematics", "department": "Science", "description": "Study of numbers, shapes, patterns, and change"},
            
            # Arts and Humanities
            {"course_name": "English Literature", "department": "Arts", "description": "Study of literature written in the English language"},
            {"course_name": "History", "department": "Arts", "description": "Study of past events and human societies"},
            {"course_name": "Philosophy", "department": "Arts", "description": "Study of fundamental questions about knowledge, existence, and values"},
            {"course_name": "Fine Arts", "department": "Arts", "description": "Visual arts, music, dance, and theater"},
            {"course_name": "Languages", "department": "Arts", "description": "Study of foreign languages and linguistics"},
            
            # Health Sciences
            {"course_name": "Medicine", "department": "Health", "description": "Study of diagnosing, treating, and preventing illness"},
            {"course_name": "Nursing", "department": "Health", "description": "Healthcare and patient care"},
            {"course_name": "Psychology", "department": "Health", "description": "Study of mind and behavior"},
            {"course_name": "Public Health", "department": "Health", "description": "Prevention of disease and promotion of health"},
            {"course_name": "Pharmacy", "department": "Health", "description": "Preparation and dispensing of medicinal drugs"},
        ]
        
        # Create interests
        interest_count = 0
        for interest_data in interests:
            interest, created = Interest.objects.get_or_create(
                name=interest_data["name"],
                defaults={"description": interest_data["description"]}
            )
            if created:
                interest_count += 1
        
        # Create courses
        course_count = 0
        for course_data in courses:
            course, created = Course.objects.get_or_create(
                course_name=course_data["course_name"],
                defaults={
                    "department": course_data["department"],
                    "description": course_data["description"]
                }
            )
            if created:
                course_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added {interest_count} interests and {course_count} courses'
            )
        ) 
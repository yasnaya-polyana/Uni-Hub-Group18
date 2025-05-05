from django.apps import AppConfig
from django.db.utils import IntegrityError, ProgrammingError

from config import Config



class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from .models import CustomUser, Interest, Course  # Add these imports
        config = Config.config["users"]

        init_with = config["init_with"]

        for user_data in init_with:
            print(user_data["username"])
            try:
                username = user_data["username"]
                password = user_data["password"]

                if user_data["email"].endswith("@"):
                    user_data["email"] = (
                        user_data["email"] + Config.config["email_domain"]
                    )

                user = CustomUser(**user_data)
                user.set_password(password)
                user.save()
                print(f"Created @{username} user.")
            except IntegrityError:
                pass
            except ProgrammingError:
                pass
        
        # Initialize interests
        if 'interests' in Config.config and 'init_with' in Config.config['interests']:
            for interest_data in Config.config['interests']['init_with']:
                try:
                    interest, created = Interest.objects.get_or_create(
                        name=interest_data["name"],
                        defaults={"description": interest_data.get("description", "")}
                    )
                    if created:
                        print(f"Created interest: {interest.name}")
                except (IntegrityError, ProgrammingError):
                    pass

        # Initialize courses
        if 'courses' in Config.config and 'init_with' in Config.config['courses']:
            for course_data in Config.config['courses']['init_with']:
                try:
                    course, created = Course.objects.get_or_create(
                        course_name=course_data["course_name"],
                        defaults={
                            "department": course_data.get("department", ""),
                            "description": course_data.get("description", "")
                        }
                    )
                    if created:
                        print(f"Created course: {course.course_name}")
                except (IntegrityError, ProgrammingError):
                    pass
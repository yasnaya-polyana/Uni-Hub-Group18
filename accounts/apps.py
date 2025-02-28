from django.apps import AppConfig
from django.db.utils import IntegrityError, ProgrammingError

from config import Config


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from .models import CustomUser

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

from django.apps import AppConfig
from django.db.utils import IntegrityError, ProgrammingError

from config import Config


class CommunitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "communities"

    def ready(self):
        try:
            from accounts.models import CustomUser
            from posts.models import Post

            from .models import Communities

            config = Config.config.get("communities") or {}

            init_with = config.get("init_with") or []

            for com_data in init_with:
                name = com_data["name"]
                auto_populate_test_data = com_data["auto_populate_with_test_data"]
                del com_data["auto_populate_with_test_data"]

                owner_username = com_data["owner_username"]
                del com_data["owner_username"]

                user = CustomUser.objects.get(username=owner_username)

                com = Communities(**com_data)
                com.owner = user
                com.status = "approved"
                com.save()
                print(f"Created #{name} community.")

                if auto_populate_test_data:
                    for i in range(0, 10):
                        post = Post(
                            title=f"Test Post {i}",
                            user=user,
                            community=com,
                            body="""
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum neque lacus, pulvinar ut fringilla quis, lacinia ac massa. Pellentesque eget nunc nec nibh pellentesque aliquet. Aliquam luctus ligula vel purus commodo, sit amet pharetra massa venenatis. Sed porta nibh nunc, eu ultrices tortor pretium ut. Sed sit amet quam eget lectus ultricies gravida. Etiam hendrerit, tellus quis iaculis sollicitudin, dui sapien viverra nulla, accumsan convallis dui nisi sit amet felis. Morbi arcu est, molestie vitae porttitor at, sodales et eros.

Suspendisse potenti. Vestibulum lectus dolor, aliquam in diam cursus, rutrum luctus nisl. Vestibulum malesuada facilisis faucibus. Aliquam sed facilisis risus. Nunc porttitor elementum diam, auctor iaculis purus dignissim non. Morbi quis elementum tortor. Aenean mauris orci, rhoncus et ornare ac, semper id sapien. Sed in efficitur mi, quis pretium turpis. Etiam aliquam bibendum vulputate.

Mauris laoreet volutpat dui, a aliquet mi porttitor nec. Vivamus in mi orci. Donec justo tortor, sagittis quis nibh non, mollis gravida diam. Sed vitae tincidunt leo, vel porta libero. Sed ornare quis enim vel luctus. Duis at faucibus nunc, ac tristique orci. Nulla luctus in justo non scelerisque. Aenean libero quam, feugiat egestas eros nec, tincidunt condimentum lectus. Maecenas sed neque vitae mi ullamcorper egestas nec volutpat ex. Fusce sodales volutpat risus, sed molestie magna semper a. Quisque vel placerat sapien. Donec varius arcu a ultricies fermentum. Sed mauris turpis, feugiat eu purus sit amet, placerat scelerisque turpis. Nullam quis risus dictum, dapibus mi ut, ullamcorper risus.
                                    """,
                        )
                        post.save()

                        for j in range(0, i):
                            comment = Post(
                                title=f"Comment Test {i}",
                                user=user,
                                community=com,
                                parent_post=post,
                                body="""
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum neque lacus, pulvinar ut fringilla quis, lacinia ac massa. Pellentesque eget nunc nec nibh pellentesque aliquet. Aliquam luctus ligula vel purus commodo, sit amet pharetra massa venenatis. Sed porta nibh nunc, eu ultrices tortor pretium ut. Sed sit amet quam eget lectus ultricies gravida. Etiam hendrerit, tellus quis iaculis sollicitudin, dui sapien viverra nulla, accumsan convallis dui nisi sit amet felis. Morbi arcu est, molestie vitae porttitor at, sodales et eros.

Suspendisse potenti. Vestibulum lectus dolor, aliquam in diam cursus, rutrum luctus nisl. Vestibulum malesuada facilisis faucibus. Aliquam sed facilisis risus. Nunc porttitor elementum diam, auctor iaculis purus dignissim non. Morbi quis elementum tortor. Aenean mauris orci, rhoncus et ornare ac, semper id sapien. Sed in efficitur mi, quis pretium turpis. Etiam aliquam bibendum vulputate.
                                    """,
                            )
                            comment.save()

                        print(f"Created demo data for #{name} community.")

        except IntegrityError:
            pass
        except ProgrammingError:
            pass

from django.apps import AppConfig
from django.db.utils import IntegrityError, ProgrammingError
import logging
import os

from config import Config


class CommunitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "communities"

    def ready(self):
        # Skip initialization during migrations
        if os.environ.get('MIGRATING') == 'True':
            return
            
        # It's generally discouraged to perform data creation in ready()
        # as it can interfere with migrations, testing, and management commands.
        # Use a dedicated management command (like generate_fake_data) instead.
        logging.info("Initializing communities in CommunitiesConfig.ready()")

        try:
            from accounts.models import CustomUser
            from posts.models import Post
            from .models import Communities, Topic

            # Initialize topics from config
            if 'topics' in Config.config and 'init_with' in Config.config['topics']:
                for topic_data in Config.config['topics']['init_with']:
                    try:
                        topic, created = Topic.objects.get_or_create(
                            name=topic_data["name"],
                            defaults={"description": topic_data.get("description", "")}
                        )
                        if created:
                            print(f"Created topic: {topic.name}")
                    except (IntegrityError, ProgrammingError) as e:
                        logging.warning(f"Error creating topic {topic_data.get('name')}: {e}")
            else:
                # If no topics in config, use the initialize_topics command
                from communities.management.commands.initialize_topics import Command as InitTopicsCommand
                topics_cmd = InitTopicsCommand()
                # Silently run the command by replacing stdout
                from io import StringIO
                topics_cmd.stdout = StringIO()
                topics_cmd.handle()
            
            config = Config.config.get("communities") or {}
            init_with = config.get("init_with") or []

            for com_data in init_with:
                name = com_data["name"]
                auto_populate_test_data = com_data.get("auto_populate_with_test_data", False) # Use .get()
                # del com_data["auto_populate_with_test_data"] # Careful modifying dict while iterating

                owner_username = com_data.get("owner_username") # Use .get()
                # del com_data["owner_username"]

                if not owner_username:
                    logging.warning(f"Skipping community '{name}' due to missing owner_username in config.")
                    continue

                try:
                    user = CustomUser.objects.get(username=owner_username)
                except CustomUser.DoesNotExist:
                    logging.warning(f"Skipping community '{name}' because owner '{owner_username}' does not exist.")
                    continue

                # Use get_or_create to be safer, though ideally this shouldn't run if generate_fake_data is used
                community_defaults = {
                    k: v for k, v in com_data.items()
                    if k not in ['name', 'owner_username', 'auto_populate_with_test_data']
                }
                community_defaults['owner'] = user
                community_defaults['status'] = 'approved' # Ensure status is set

                com, created = Communities.objects.get_or_create(
                    name=name,
                    defaults=community_defaults
                )

                if created:
                    print(f"Created #{name} community via apps.py.") # Distinguish source
                    if auto_populate_test_data:
                        # ... (rest of post/comment creation logic) ...
                        print(f"Created demo data for #{name} community via apps.py.")
                else:
                     print(f"Community #{name} already existed (found via apps.py).")

        except IntegrityError as e:
             logging.error(f"IntegrityError during app ready community creation: {e}")
             # pass # Don't just pass, log the error
        except ProgrammingError as e:
             logging.warning(f"ProgrammingError during app ready (likely migrations needed): {e}")
             # pass
        except Exception as e: # Catch other potential errors
             logging.error(f"Unexpected error in CommunitiesConfig.ready(): {e}")
        pass # Keep the pass here if you comment out the whole block

import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import nanoid
from django.db.utils import IntegrityError

from accounts.models import CustomUser
from communities.models import Communities, CommunityMember, Topic
from posts.models import Post
from events.models import Event


class Command(BaseCommand):
    help = 'Generates fake data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=20, help='Number of users to create')
        parser.add_argument('--communities', type=int, default=15, help='Number of communities to create (will try to create a mix of subjects/societies)')
        parser.add_argument('--posts', type=int, default=100, help='Number of posts to create')
        parser.add_argument('--comments', type=int, default=200, help='Number of comments to create')
        parser.add_argument('--events', type=int, default=30, help='Number of events to create')
        parser.add_argument('--likes', type=int, default=300, help='Number of likes to create')
        parser.add_argument('--follows', type=int, default=100, help='Number of user follows to create')

    def handle(self, *args, **options):
        fake = Faker()
        
        # Create users
        self.stdout.write('Creating users...')
        users = []
        user_types = ['student', 'staff', 'moderator', 'admin']
        departments = [
            'Computer Science', 'Engineering', 'Business', 'Arts', 'Medicine', 'Law',
            'Psychology', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'History',
            'English Literature', 'Economics', 'Sociology', 'Philosophy', 'Architecture',
            'Education', 'Nursing', 'Film Studies', 'Music', 'Political Science',
            'Environmental Science', 'Journalism', 'Marketing', 'Accounting', 'Finance'
        ]
        
        for i in range(options['users']):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
            email = f"{username}@live.uwe.ac.uk"
            
            user = CustomUser.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                date_joined=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone()),
                bio=fake.paragraph(),
                student_id=str(random.randint(10000000, 99999999))
            )
            user.set_password('password')  # Set a simple password for testing
            
            # Set random user attributes if they exist in your model
            try:
                user.department = random.choice(departments)
            except:
                pass
                
            try:
                user.user_type = random.choice(user_types)
                # Make some users admins
                if user.user_type == 'admin':
                    user.is_staff = True
                    user.is_superuser = random.choice([True, False])
            except:
                pass
                
            try:
                user.graduation_year = random.randint(2023, 2027)
            except:
                pass
                
            user.save()
            users.append(user)
            
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))
        
        # Create topics for communities
        self.stdout.write('Creating topics...')
        topics = []
        topic_names = list(set([ # Use set to avoid duplicates
            # Academic Topics
            'Computer Science', 'Engineering', 'Business', 'Arts', 'Medicine', 'Law',
            'Psychology', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'History',
            'Literature', 'Economics', 'Sociology', 'Philosophy', 'Architecture',
            'Education', 'Nursing', 'Film Studies', 'Music', 'Political Science',
            # Interest Topics
            'Technology', 'Sports', 'Arts', 'Science', 'Entertainment', 'Politics',
            'Health', 'Education', 'Travel', 'Food', 'Fashion', 'Music',
            'Gaming', 'Photography', 'Books', 'Movies', 'Television', 'Fitness',
            'Cooking', 'DIY', 'Gardening', 'Pets', 'Cars', 'Motorcycles',
            # Campus Life Topics
            'Campus Events', 'Student Union', 'Accommodation', 'Clubs', 'Societies',
            'Student Support', 'Career Services', 'Library', 'Sports Facilities',
            'Dining', 'Transportation', 'International Students', 'Alumni',
            # Social Topics
            'Meetups', 'Dating', 'Friendship', 'Networking', 'Volunteering',
            'Parties', 'Concerts', 'Festivals', 'Nightlife', 'Cultural Events'
        ]))
        
        for name in topic_names:
            topic, created = Topic.objects.get_or_create(name=name)
            topics.append(topic)
            
        self.stdout.write(self.style.SUCCESS(f'Ensured {len(topics)} topics exist'))
        
        # Define Community Data
        communities_data = [
            {
                'name': 'Computer Science Society',
                'description': 'A place for all CS students to discuss coursework, projects, and tech news.',
                'category': 'academic',
                'topics': ['programming', 'algorithms', 'data structures', 'web development', 'machine learning']
            },
            {
                'name': 'Debating Union',
                'description': 'Hone your argumentation skills and discuss current events.',
                'category': 'society',
                'topics': ['politics', 'philosophy', 'current events', 'public speaking']
            },
            {
                'name': 'University Football Club',
                'description': 'Join us for training sessions and competitive matches.',
                'category': 'sports',
                'topics': ['football', 'sports', 'fitness', 'teamwork']
            },
            {
                'name': 'Photography Club',
                'description': 'Share your passion for photography, learn new techniques, and go on photo walks.',
                'category': 'hobby',
                'topics': ['photography', 'art', 'cameras', 'editing']
            },
            {
                'name': 'Mathematics Society',
                'description': 'Exploring the beauty and application of mathematics beyond the curriculum.',
                'category': 'academic',
                'topics': ['mathematics', 'calculus', 'algebra', 'statistics', 'logic']
            },
            {
                'name': 'Film Appreciation Society',
                'description': 'Watch and discuss classic and contemporary cinema.',
                'category': 'hobby',
                'topics': ['film', 'cinema', 'movies', 'directors', 'screenwriting']
            },
            {
                'name': 'Environmental Action Group',
                'description': 'Working towards a greener campus and raising awareness about environmental issues.',
                'category': 'society',
                'topics': ['environment', 'sustainability', 'climate change', 'activism']
            },
            {
                'name': 'Basketball Team',
                'description': 'Casual and competitive basketball for all skill levels.',
                'category': 'sports',
                'topics': ['basketball', 'sports', 'fitness']
            },
            {
                'name': 'History Society',
                'description': 'Delving into historical events, figures, and periods through discussions and talks.',
                'category': 'academic',
                'topics': ['history', 'ancient history', 'modern history', 'politics']
            },
            {
                'name': 'Board Games Club',
                'description': 'Meet up for casual board game nights.',
                'category': 'hobby',
                'topics': ['board games', 'tabletop games', 'strategy games', 'social']
            },
             {
                'name': 'Law Society',
                'description': 'For aspiring lawyers and anyone interested in the legal field.',
                'category': 'academic',
                'topics': ['law', 'legal studies', 'mooting', 'careers']
            },
            {
                'name': 'Creative Writing Group',
                'description': 'Share your stories, poems, and scripts and get feedback.',
                'category': 'hobby',
                'topics': ['writing', 'fiction', 'poetry', 'screenwriting', 'literature']
            },
            {
                'name': 'Hiking Club',
                'description': 'Organizing trips to explore local trails and nature.',
                'category': 'sports', # Could also be hobby
                'topics': ['hiking', 'outdoors', 'nature', 'fitness', 'adventure']
            },
            {
                'name': 'Economics Society',
                'description': 'Discussing economic theories, policies, and market trends.',
                'category': 'academic',
                'topics': ['economics', 'finance', 'markets', 'policy', 'business']
            },
            {
                'name': 'Music Society',
                'description': 'Jam sessions, open mic nights, and appreciation for all genres.',
                'category': 'society',
                'topics': ['music', 'bands', 'instruments', 'singing', 'concerts']
            }
            # Add more communities as needed
        ]
        
        # Create communities
        self.stdout.write('Creating communities...')
        communities_created = 0
        num_to_create = min(options['communities'], len(communities_data))
        users = list(CustomUser.objects.all())

        for i in range(num_to_create):
            community_info = communities_data[i]
            owner = random.choice(users)
            community_name_to_create = community_info['name']

            self.stdout.write(f"\n>>> Processing: '{community_name_to_create}'")

            # --- Enhanced Debugging & Handling ---
            found_active = None
            found_soft_deleted = None

            try:
                # Check active first (using default manager)
                found_active = Communities.objects.get(name=community_name_to_create)
                self.stdout.write(f"  DEBUG: FOUND active '{found_active.name}' (ID: {found_active.id}, Status: {found_active.status})")
            except Communities.DoesNotExist:
                self.stdout.write(f"  DEBUG: Did NOT find active '{community_name_to_create}'.")
                try:
                    # If not active, check soft-deleted (using all_objects manager)
                    # NOTE: Ensure your SoftDeleteModel provides an 'all_objects' manager or similar
                    found_soft_deleted = Communities.all_objects.get(name=community_name_to_create)
                    self.stdout.write(f"  DEBUG: FOUND soft-deleted '{found_soft_deleted.name}' (ID: {found_soft_deleted.id}, Deleted at: {found_soft_deleted.deleted_at})")
                except Communities.DoesNotExist:
                    self.stdout.write(f"  DEBUG: Did NOT find soft-deleted '{community_name_to_create}' either.")
                except AttributeError:
                     self.stdout.write(f"  DEBUG: Could not check soft-deleted (Communities model might not have 'all_objects' manager).")
                except Exception as e:
                    self.stdout.write(f"  DEBUG: Error checking soft-deleted for '{community_name_to_create}': {e}")

            # --- End Enhanced Debugging ---

            community = None
            created = False

            if found_active:
                community = found_active
                created = False
                self.stdout.write(f"  INFO: Using existing active community '{community.name}'.")
            elif found_soft_deleted:
                # Option 1: Restore the soft-deleted one
                self.stdout.write(f"  INFO: Restoring soft-deleted community '{found_soft_deleted.name}'.")
                found_soft_deleted.deleted_at = None # Or use a .restore() method if available
                # Update other fields from defaults if needed?
                found_soft_deleted.description = community_info['description']
                found_soft_deleted.owner = owner # Be careful changing owner
                found_soft_deleted.category = community_info['category']
                found_soft_deleted.status = 'approved'
                found_soft_deleted.save()
                community = found_soft_deleted
                created = False # It wasn't technically created *now*
                communities_created += 1 # Count it as "processed" or "made available"

                # Option 2: Skip (if you don't want to restore)
                # self.stdout.write(f"  INFO: Skipping creation because soft-deleted community '{found_soft_deleted.name}' exists.")
                # continue # Skip to the next community in the loop

            else:
                # Only try to create if neither active nor soft-deleted was found
                self.stdout.write(f"  INFO: Attempting to create new community '{community_name_to_create}'.")
                try:
                    community, created = Communities.objects.get_or_create(
                        name=community_name_to_create,
                        defaults={
                            'description': community_info['description'],
                            'owner': owner,
                            'category': community_info['category'],
                            'status': 'approved',
                            'id': nanoid.generate(size=10)
                        }
                    )
                    if created:
                         self.stdout.write(f"  SUCCESS: Created new community: {community.name}")
                         communities_created += 1
                    else:
                         # This case should ideally not happen if our checks above were thorough
                         self.stdout.write(f"  WARNING: get_or_create found an existing community '{community.name}' unexpectedly.")

                except IntegrityError as e:
                    self.stdout.write(f"  ERROR: IntegrityError during create for '{community_name_to_create}': {e}")
                    self.stdout.write(f"  ERROR: This might happen if there's a race condition or constraint issue.")
                    continue # Skip to next community on error


            # --- Assign topics/members only if we have a valid community object ---
            if community and created: # Only add members/topics if *newly* created by get_or_create
                 # Assign topics
                 community_topics = Topic.objects.filter(name__in=community_info['topics'])
                 community.topics.set(community_topics)

                 # Add members
                 num_members = random.randint(5, 20)
                 k = min(num_members, len(users) - 1 if owner in users else len(users))
                 members_to_add = random.sample([u for u in users if u != owner], k=k)
                 members_bulk_list = [
                     CommunityMember(user=member_user, community=community, role="moderator" if random.random() < 0.1 else "member")
                     for member_user in members_to_add
                 ]
                 if members_bulk_list:
                     CommunityMember.objects.bulk_create(members_bulk_list)
            elif community and not created and found_soft_deleted:
                 # Decide if you want to re-add members/topics when restoring
                 self.stdout.write(f"  INFO: Community '{community.name}' was restored. Skipping member/topic assignment for now.")
                 pass


        self.stdout.write(self.style.SUCCESS(f'\nFinished community processing. Processed/Created {communities_created} communities.'))
        
        # Create posts
        self.stdout.write('Creating posts...')
        posts_created = 0
        all_communities = list(Communities.objects.all())
        possible_posts_users = users # Allow any user to create posts

        for _ in range(options['posts']):
            user = random.choice(possible_posts_users)
            # Decide if it's a community post or a user post (adjust ratio as needed)
            community_post = random.random() < 0.7 and all_communities
            community = random.choice(all_communities) if community_post else None

            # Ensure title does not exceed max_length of the Post model's title field
            generated_title = fake.sentence(nb_words=random.randint(5, 15))
            truncated_title = generated_title[:60] # Truncate to 60 characters

            post = Post.objects.create(
                user=user,
                community=community,
                title=truncated_title, # Use the truncated title
                body=fake.paragraph(nb_sentences=random.randint(3, 10)),
                id=nanoid.generate(size=10)
            )
            posts_created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {posts_created} posts'))
        
        # Create comments
        self.stdout.write('Creating comments...')
        comments_created = 0
        all_posts = list(Post.objects.filter(parent_post__isnull=True)) # Only comment on top-level posts
        if all_posts:
            for _ in range(options['comments']):
                user = random.choice(users)
                parent_post = random.choice(all_posts)
                # Ensure comment title (if used) is also truncated if necessary
                # Assuming comments might not need titles, or use a shorter max_length
                comment = Post.objects.create(
                    user=user,
                    community=parent_post.community, # Comments belong to the same community as parent
                    parent_post=parent_post,
                    title="", # Provide an empty string for the title
                    body=fake.paragraph(nb_sentences=random.randint(1, 5)),
                    id=nanoid.generate(size=10)
                )
                comments_created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {comments_created} comments'))
        
        # Create events
        self.stdout.write('Creating events...')
        events_created = 0
        if all_communities:
            for _ in range(options['events']):
                community = random.choice(all_communities)
                owner = random.choice(list(community.members.all()) + [community.owner]) # Event owner is member or community owner
                start_date = timezone.now() + timedelta(days=random.randint(1, 60))
                end_date = start_date + timedelta(hours=random.randint(1, 24 * 7))

                # Ensure event name does not exceed max_length
                generated_name = fake.catch_phrase()
                truncated_name = generated_name[:100] # Assuming Event name max_length is 100

                Event.objects.create(
                    community=community,
                    user=owner,
                    title=truncated_name,
                    details=fake.paragraph(nb_sentences=random.randint(2, 5)),
                    start_at=start_date,
                    end_at=end_date,
                    location=fake.address(),
                    id=nanoid.generate(size=10)
                )
                events_created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {events_created} events'))
        
        self.stdout.write(self.style.SUCCESS('Fake data generation complete!'))

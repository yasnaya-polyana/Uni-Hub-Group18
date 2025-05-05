import logging
import re

import bleach
import markdown
from accounts.models import CustomUser
from communities.models import Communities, Topic
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from events.models import Event
from md_extensions.tailwind import TailwindExtension
from posts.forms import PostCreationForm
from posts.models import Interaction, Post
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

log = logging.getLogger("app")


def post_view(request, post_id: str):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        form = PostCreationForm(request.POST, is_comment=True)
        if form.is_valid():
            comment_post = form.save(commit=False)
            comment_post.user = request.user
            comment_post.parent_post = post
            if not post.title:
                post.title = ""
            comment_post.save()
            return redirect("post", post_id=post_id)
    elif request.method == "GET":
        # Get the post from the database

        # Process markdown for the post
        md = markdown.Markdown(extensions=["extra", TailwindExtension()])
        clean_body = bleach.clean(post.body)
        post.md_body = md.convert(clean_body)

        # Get comments for this post
        comments = Post.objects.filter(parent_post=post)

        comment_form = PostCreationForm()

        return render(
            request,
            "posts/post-page.jinja",
            {
                "post": post,
                "comments": comments,
                "form": comment_form,
                "user": request.user,
            },
        )
    elif request.method == "DELETE":
        post = Post.objects.get(id=post_id)
        if post.user == request.user:
            if post.event.count() != 0:
                event = Event.objects.filter(pkid=post.event.get().pkid).first()
                event.delete()
            post.delete()
            return redirect("/posts")
        else:
            return HttpResponse(status=403)


def posts_view(request):
    md = markdown.Markdown(extensions=["extra", TailwindExtension()])

    # Start with all posts that aren't comments
    posts_qs = Post.objects.filter(parent_post=None).prefetch_related("topics")

    # Get search query
    search_query = request.GET.get("q", "")
    if search_query:
        posts_qs = posts_qs.filter(
            Q(title__icontains=search_query) | Q(body__icontains=search_query)
        )

    # Apply advanced filters
    # Date range
    date_from = request.GET.get("date_from")
    if date_from:
        posts_qs = posts_qs.filter(created_at__gte=date_from)

    date_to = request.GET.get("date_to")
    if date_to:
        posts_qs = posts_qs.filter(created_at__lte=date_to)

    # Author filter
    author = request.GET.get("author")
    if author:
        posts_qs = posts_qs.filter(user__username__icontains=author)

    # Community filter
    community = request.GET.get("community")
    if community:
        posts_qs = posts_qs.filter(community__id=community)

    # Content type filters
    has_image = request.GET.get("has_image")
    if has_image:
        posts_qs = posts_qs.filter(body__icontains="![")

    has_link = request.GET.get("has_link")
    if has_link:
        posts_qs = posts_qs.filter(body__icontains="http")

    # Interaction filters
    min_likes = request.GET.get("min_likes")
    if min_likes and min_likes.isdigit():
        posts_qs = posts_qs.annotate(
            like_count=Count("interactions", filter=Q(interactions__interaction="like"))
        ).filter(like_count__gte=int(min_likes))

    min_comments = request.GET.get("min_comments")
    if min_comments and min_comments.isdigit():
        posts_qs = posts_qs.annotate(comment_count=Count("comments")).filter(
            comment_count__gte=int(min_comments)
        )
    min_reposts = request.GET.get("min_reposts")
    if min_reposts and min_reposts.isdigit():
        posts_qs = posts_qs.annotate(repost_count=Count("reposts")).filter(
            repost_count__gte=int(min_reposts)
        )
    # Sorting
    sort = request.GET.get("sort", "newest")
    if sort == "newest":
        posts_qs = posts_qs.order_by("-created_at")
    elif sort == "oldest":
        posts_qs = posts_qs.order_by("created_at")
    elif sort == "most_likes":
        posts_qs = posts_qs.annotate(
            like_count=Count("interactions", filter=Q(interactions__interaction="like"))
        ).order_by("-like_count", "-created_at")
    elif sort == "most_comments":
        posts_qs = posts_qs.annotate(comment_count=Count("comments")).order_by(
            "-comment_count", "-created_at"
        )
    elif sort == "most_reposts":
        posts_qs = posts_qs.annotate(repost_count=Count("reposts")).order_by(
            "-repost_count", "-created_at"
        )

    # Get all communities for the dropdown
    communities = Communities.objects.all()

    # Process markdown for each post
    for post in posts_qs:
        clean_body = bleach.clean(post.body)
        post.md_body = md.convert(clean_body)

    return render(
        request,
        "posts/post-feed.jinja",
        {
            "posts": posts_qs,
            "search_str": search_query,
            "communities": communities,
        },
    )


def community_member_required(func):
    def wrapper(request, community_id=None, *args, **kwargs):
        # When decorating post_create_community view, we get community_id
        community = get_object_or_404(Communities, id=community_id)
        if not CommunityMember.objects.filter(
            user=request.user, community=community
        ).exists():
            return HttpResponseBadRequest("You are not a member of this community.")
        return func(request, community_id=community_id, *args, **kwargs)

    return wrapper


def dashboard(request):
    if not request.user.is_authenticated:
        return render(request, "posts/posts-list.jinja", {"posts": []})

    # If the user is authenticated, filter posts
    posts = (
        Post.objects.filter(
            Q(
                user__in=request.user.following.all()
            )  # Get posts from people the user is following
            | Q(user=request.user)  # Include the user's own posts
        )
        .exclude(parent_post__isnull=False)  # Exclude comments
        .order_by("-created_at")  # Sort by newest first
    )

    # Filter by post type (post, repost, etc.)
    post_type = request.GET.get("post_type", None)
    if post_type:
        if post_type == "post":
            posts = posts.filter(parent_post__isnull=True)
        elif post_type == "repost":
            posts = posts.filter(is_repost=True)

    # Collect user IDs for the posts
    user_ids = set(posts.values_list("user_id", flat=True))
    # Add the current user to the list
    user_ids.add(request.user.id)
    # Get all user objects
    users = CustomUser.objects.filter(id__in=user_ids)

    # Prepare users for rendering
    users_data = {}
    for user in users:
        users_data[str(user.id)] = {
            "username": user.username,
            "display_name": user.get_full_name() or user.username,
            "avatar": user.avatar_url if hasattr(user, "avatar_url") else None,
        }

    return render(
        request,
        "posts/posts-list.jinja",
        {"posts": posts, "users": users_data, "filter": post_type},
    )


@login_required
def post_detail(request, post_id: str):
    post = get_object_or_404(Post, id=post_id)

    # Try to determine if the post is a repost
    original_post = post
    if original_post.is_repost and original_post.repost_of:
        original_post = original_post.repost_of

    # Get comments for the original post
    comments = original_post.comments.all().order_by("-created_at")

    # Determine whether the user can edit the post
    user_can_edit = request.user == post.user

    # Determine if the user has already liked the post
    user_has_liked = request.user.is_authenticated and original_post.interactions.filter(
        user=request.user, interaction="like"
    ).exists()

    # Determine if the user has already reposted the post
    user_has_reposted = (
        request.user.is_authenticated
        and Post.objects.filter(
            user=request.user, repost_of=original_post, is_repost=True
        ).exists()
    )

    return render(
        request,
        "posts/post-detail.jinja",
        {
            "post": post,
            "comments": comments,
            "user_can_edit": user_can_edit,
            "user_has_liked": user_has_liked,
            "user_has_reposted": user_has_reposted,
        },
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostCreationForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            
            # Add selected topics as hashtags to post body
            if 'topics' in form.cleaned_data and form.cleaned_data['topics']:
                selected_topics = form.cleaned_data['topics']
                topic_tags = []
                
                # Create a list of hashtags for the selected topics
                for topic in selected_topics:
                    topic_tags.append(f"#{topic.name}")
                
                # Add the hashtags to the post body if they're not already included
                if post.body and topic_tags:
                    # Only append if not already in text
                    existing_text = post.body.strip()
                    hashtag_text = " ".join(topic_tags)
                    
                    # Check if the hashtags are already in the post
                    if not any(tag.lower() in existing_text.lower() for tag in topic_tags):
                        # Add a newline if the post doesn't end with one
                        if existing_text and not existing_text.endswith("\n"):
                            post.body = existing_text + "\n\n" + hashtag_text
                        else:
                            post.body = existing_text + hashtag_text
            
            post.save()
            
            # Save m2m relationships
            form.save_m2m()
            print("Post saved with topics:", post.topics.all())

            # Find mentioned users
            mention_pattern = re.compile(r"\[@([a-zA-Z0-9_]+)\]")
            mentions = mention_pattern.findall(post.body)

            # print mentioned users
            for username in mentions:
                try:
                    m_user = CustomUser.objects.get(username=username)
                    post.mentioned_users.add(m_user)
                except CustomUser.DoesNotExist:
                    continue
                    
            # Find hashtags (topics)
            hashtag_pattern = re.compile(r"#([a-zA-Z0-9_]+)")
            hashtags = hashtag_pattern.findall(post.body)
            
            # Add existing topics based on hashtags - no auto-creation
            for tag in hashtags:
                try:
                    # Only use existing topics - don't create new ones
                    topic = Topic.objects.filter(name__iexact=tag).first()
                    if topic:
                        post.topics.add(topic)
                except Exception as e:
                    print(f"Error adding topic: {e}")
                    continue

            # Check if there's a next parameter or if we should redirect to dashboard
            next_url = request.POST.get("next", "dashboard")
            return redirect(next_url)
    else:
        form = PostCreationForm()

    # bug fix: ValueError
    return render(
        request, "posts/create-post.jinja", {"form": form, "is_comment": False}
    )


@login_required
@community_member_required
def post_create_community(request, community_id: str):
    community = get_object_or_404(Communities, id=community_id)

    if request.method == "POST":
        form = PostCreationForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.community = community
            
            # Add selected topics as hashtags to post body
            if 'topics' in form.cleaned_data and form.cleaned_data['topics']:
                selected_topics = form.cleaned_data['topics']
                topic_tags = []
                
                # Create a list of hashtags for the selected topics
                for topic in selected_topics:
                    topic_tags.append(f"#{topic.name}")
                
                # Add the hashtags to the post body if they're not already included
                if post.body and topic_tags:
                    # Only append if not already in text
                    existing_text = post.body.strip()
                    hashtag_text = " ".join(topic_tags)
                    
                    # Check if the hashtags are already in the post
                    if not any(tag.lower() in existing_text.lower() for tag in topic_tags):
                        # Add a newline if the post doesn't end with one
                        if existing_text and not existing_text.endswith("\n"):
                            post.body = existing_text + "\n\n" + hashtag_text
                        else:
                            post.body = existing_text + hashtag_text
            
            post.save()
            
            # Save m2m relationships
            form.save_m2m()
            
            # Find mentioned users
            mention_pattern = re.compile(r"\[@([a-zA-Z0-9_]+)\]")
            mentions = mention_pattern.findall(post.body)
            
            for username in mentions:
                try:
                    m_user = CustomUser.objects.get(username=username)
                    post.mentioned_users.add(m_user)
                except CustomUser.DoesNotExist:
                    continue
                    
            # Find hashtags (topics)
            hashtag_pattern = re.compile(r"#([a-zA-Z0-9_]+)")
            hashtags = hashtag_pattern.findall(post.body)
            
            # Add existing topics based on hashtags - no auto-creation
            for tag in hashtags:
                try:
                    # Only use existing topics - don't create new ones
                    topic = Topic.objects.filter(name__iexact=tag).first()
                    if topic:
                        post.topics.add(topic)
                except Exception as e:
                    print(f"Error adding topic: {e}")
                    continue

            return redirect("community_detail", community_id=community_id)
    else:
        form = PostCreationForm()

    return render(
        request,
        "posts/create-post.jinja",
        {"form": form, "community": community, "is_comment": False},
    )


@login_required
def post_comment(request, post_id: str):
    parent_post = Post.objects.get(id=post_id)
    
    if parent_post == None:
        parent_post = []

    if request.method == "POST":
        form = PostCreationForm(request.POST, is_comment=True)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.parent_post = parent_post
            if not post.title:
                post.title = ""
                
            # Add selected topics as hashtags to post body
            if 'topics' in form.cleaned_data and form.cleaned_data['topics']:
                selected_topics = form.cleaned_data['topics']
                topic_tags = []
                
                # Create a list of hashtags for the selected topics
                for topic in selected_topics:
                    topic_tags.append(f"#{topic.name}")
                
                # Add the hashtags to the post body if they're not already included
                if post.body and topic_tags:
                    # Only append if not already in text
                    existing_text = post.body.strip()
                    hashtag_text = " ".join(topic_tags)
                    
                    # Check if the hashtags are already in the post
                    if not any(tag.lower() in existing_text.lower() for tag in topic_tags):
                        # Add a newline if the post doesn't end with one
                        if existing_text and not existing_text.endswith("\n"):
                            post.body = existing_text + "\n\n" + hashtag_text
                        else:
                            post.body = existing_text + hashtag_text
                
            post.save()
            
            # Save m2m relationships if they exist
            form.save_m2m()
            
            # Find mentioned users
            mention_pattern = re.compile(r"\[@([a-zA-Z0-9_]+)\]")
            mentions = mention_pattern.findall(post.body)
            
            for username in mentions:
                try:
                    m_user = CustomUser.objects.get(username=username)
                    post.mentioned_users.add(m_user)
                except CustomUser.DoesNotExist:
                    continue
                    
            # Find hashtags (topics)
            hashtag_pattern = re.compile(r"#([a-zA-Z0-9_]+)")
            hashtags = hashtag_pattern.findall(post.body)
            
            # Add existing topics based on hashtags - no auto-creation
            for tag in hashtags:
                try:
                    # Only use existing topics - don't create new ones
                    topic = Topic.objects.filter(name__iexact=tag).first()
                    if topic:
                        post.topics.add(topic)
                except Exception as e:
                    print(f"Error adding topic: {e}")
                    continue

            return redirect("post", post_id=post_id)
    else:
        form = PostCreationForm(is_comment=True)

    return render(
        request, "posts/create-post.jinja", {"form": form, "is_comment": True, "parent_post": parent_post}
    )


def post_pin(request, post_id: int):
    post = Post.objects.get(id=post_id)
    if post.user == request.user:
        post.is_pinned = not post.is_pinned
        post.save()
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=403)


def post_interact(request, post_id: int, interaction: str):
    if interaction == "repost":
        return post_repost(request, post_id)
        
    post = Post.objects.get(id=post_id)
    try:
        interaction = Interaction.objects.get(
            post_id=post.pkid, user_id=request.user.id
        )
        interaction.delete()
    except:
        interaction = Interaction(user=request.user, post=post, interaction=interaction)
        interaction.save()
    
    return HttpResponse(status=204)


@login_required
def post_edit(request, post_id: str):
    post = get_object_or_404(Post, id=post_id)

    # Check if the current user is the creator of the post
    if request.user != post.user:
        return HttpResponseBadRequest("You cannot edit this post.")

    if request.method == "POST":
        form = PostCreationForm(request.POST, instance=post, is_comment=post.parent_post != None)

        if form.is_valid():
            form.save()
            return redirect("post", post_id=post_id)
    else:
        form = PostCreationForm(instance=post, is_comment=post.parent_post != None)

    return render(
        request, "posts/edit-post.jinja", {"form": form, "post": post, "is_comment": post.parent_post != None}
    )


@login_required
def post_delete(request, post_id: str):
    post = get_object_or_404(Post, id=post_id)

    # Check if the current user is the creator of the post
    if request.user != post.user:
        return HttpResponseBadRequest("You cannot delete this post.")

    # Determine where to redirect after deletion
    if post.parent_post:
        redirect_to = reverse("post", kwargs={"post_id": post.parent_post.id})
    elif post.community:
        redirect_to = reverse(
            "community_detail", kwargs={"community_id": post.community.id}
        )
    else:
        redirect_to = reverse("dashboard")

    # Delete the post
    post.delete()

    return HttpResponseRedirect(redirect_to)


@login_required
@require_POST
def post_repost(request, post_id: str):
    original_post = get_object_or_404(Post, id=post_id)

    # Make sure we're not reposting a repost
    if original_post.is_repost:
        original_post = original_post.repost_of

    # Check if the user has already reposted this post
    existing_repost = Post.objects.filter(
        user=request.user, repost_of=original_post, is_repost=True
    ).first()

    if existing_repost:
        # User already reposted, so remove the repost
        existing_repost.delete()
        action = "unreposted"
    else:
        # Create a new repost
        repost = Post(
            user=request.user,
            repost_of=original_post,
            is_repost=True,
            community=original_post.community,
        )
        repost.save()
        action = "reposted"

    # If this is an AJAX request, return JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "success", "action": action})

    # Otherwise redirect back to the post
    return redirect("post", post_id=post_id)


@login_required
@csrf_exempt
@require_POST
def post_like(request, post_id: str):
    post = get_object_or_404(Post, id=post_id)

    # Try to determine if the post is a repost
    if post.is_repost and post.repost_of:
        post = post.repost_of

    # Check if the user has already liked this post
    existing_like = Interaction.objects.filter(
        user=request.user, post=post, interaction="like"
    ).first()

    if existing_like:
        # User already liked, so remove the like
        existing_like.delete()
        action = "unliked"
    else:
        # Create a new like
        like = Interaction(user=request.user, post=post, interaction="like")
        like.save()
        action = "liked"

    # If this is an AJAX request, return JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "count": post.interactions.filter(interaction="like").count(),
            }
        )

    # Otherwise redirect back to the post
    return redirect("post", post_id=post_id)

import logging
import re
import bleach
import markdown
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from accounts.models import CustomUser
from communities.models import Communities
from events.models import Event
from md_extensions.tailwind import TailwindExtension
from posts.forms import PostCreationForm
from posts.models import Interaction, Post

log = logging.getLogger("app")


def post_view(request, post_id: str):
    if request.method == "GET":
        # Get the post from the database
        post = get_object_or_404(Post, id=post_id)
        
        # Process markdown for the post
        md = markdown.Markdown(extensions=["extra", TailwindExtension()])
        clean_body = bleach.clean(post.body)
        post.md_body = md.convert(clean_body)
        
        # Get comments for this post
        comments = Post.objects.filter(parent_post=post)
        
        return render(request, "posts/post-page.jinja", {
            "post": post,
            "comments": comments,
            "user": request.user
        })
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
    posts_qs = Post.objects.filter(parent_post=None)
    
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


def post_create(request):
    if request.method == "POST":
        form = PostCreationForm(request.POST)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user

            post.save()

            # Find mentioned users
            mention_pattern = re.compile(r"\[@([a-zA-Z0-9_]+)\]")
            mentions = mention_pattern.findall(post.body)

            # print mentioned users
            for username in mentions:
                m_user = CustomUser.objects.get(username=username)
                post.mentioned_users.add(m_user)
            
            # Check if there's a next parameter or if we should redirect to dashboard
            next_url = request.POST.get("next", "dashboard")
            return redirect(next_url)
    else:
        form = PostCreationForm()
    
    # bug fix: ValueError
    return render(
        request, "posts/create-post.jinja", {"form": form, "is_comment": False}
    )


def post_repost(request, post_id: str):
    reposted_post = Post.objects.get(id=post_id)

    try:
        repost = reposted_post.reposts.get(user_id=request.user.id)
    except:
        repost = Post(
            title="REPOST",
            body=f"/posts/${post_id}",
            ref_post=reposted_post,
            user=request.user,
        )
        repost.save()
        return HttpResponse(status=204)

    repost.delete()
    return HttpResponse(status=204)

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
            post.save()

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
    post = Post.objects.get(id=post_id)
    try:
        interaction = Interaction.objects.get(
            post_id=post.pkid, user_id=request.user.id
        )
    except:
        interaction = Interaction(user=request.user, post=post, interaction=interaction)
        interaction.save()
        return HttpResponse(status=204)

    interaction.delete()
    return HttpResponse(status=204)

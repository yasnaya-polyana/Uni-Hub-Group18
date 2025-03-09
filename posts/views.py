import logging

import bleach
import markdown
from django.http import HttpResponse
from django.shortcuts import redirect, render

from md_extensions.tailwind import TailwindExtension
from posts.forms import PostCreationForm
from posts.models import Interaction, Post

log = logging.getLogger("app")


def post_view(request, post_id: str):
    if request.method == "GET":
        post = Post.objects.get(id=post_id)
        return render(request, "posts/post-page.jinja", {"post": post})
    elif request.method == "DELETE":
        post = Post.objects.get(id=post_id)
        if post.user == request.user:
            post.delete()
            return redirect("/posts")
        else:
            return HttpResponse(status=403) 


def posts_view(request):
    md = markdown.Markdown(extensions=["fenced_code", TailwindExtension()])
    latest_posts_list = Post.objects.filter(parent_post=None).order_by("-created_at")

    for post in latest_posts_list:
        clean_body = bleach.clean(post.body)
        post.md_body = md.convert(clean_body)

    return render(request, "posts/post-feed.jinja", {"posts": latest_posts_list})


def post_create(request):
    if request.method == "POST":
        form = PostCreationForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("posts")
    else:
        form = PostCreationForm()
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

    if request.method == "POST":
        form = PostCreationForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.parent_post = parent_post
            post.save()
            return redirect("post", post_id=post_id)
    else:
        form = PostCreationForm()
    return render(
        request, "posts/create-post.jinja", {"form": form, "is_comment": True}
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

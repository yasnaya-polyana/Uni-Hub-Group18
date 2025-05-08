import json
from pprint import pprint

from accounts.models import CustomUser
from communities.models import Communities
from django.shortcuts import HttpResponse, render
from events.models import Event
from posts.models import Post


def setup(request):
    return render(request, "demo/setup.jinja")


def init_demo_data(request):
    with open("demo_data.json", "r") as f:
        data = json.load(f)

    pprint(data)

    # Communities
    communities = data["communities"]
    for community in communities:
        owner_username = community.get("owner_username")
        if not owner_username:
            raise Exception(f"owner_username missing on {community['id']} community")

        try:
            user = CustomUser.objects.get(username=owner_username)
        except CustomUser.DoesNotExist:
            raise Exception(f"{owner_username} does not exist")

        com_id = community.get("id")
        try:
            new_community = Communities.objects.get(id=com_id)
        except Exception:
            new_community = Communities(id=com_id)

        new_community.name = community.get("name")
        new_community.description = community.get("description")
        new_community.owner = user
        new_community.category = community.get("category")
        new_community.status = community.get("status")

        pprint(community)
        new_community.save()

        # Community Posts
        community_posts = community.get("posts", [])
        for post in community_posts:
            username = post.get("username")
            if not username:
                raise Exception(f"username missing")

            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                raise Exception(f"{username} does not exist")

            new_post = Post(
                title=post.get("title"),
                body=post.get("body"),
                user=user,
                community=new_community,
                is_pinned=post.get("is_pinned"),
            )
            new_post.save()

        # Community Events
        community_events = community.get("events", [])
        for event in community_events:
            username = event.get("username")
            if not username:
                raise Exception("username missing")

            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                raise Exception(f"{username} does not exist")

            # Create a post for the event
            new_event_post = Post(
                title=event.get("title"),
                body=event.get("details"),
                user=user,
                community=new_community,
            )
            new_event_post.save()

            new_event = Event(
                post=new_event_post,
                user=user,
                community=new_community,
                location=event.get("location"),
                start_at=event.get("start_at"),
                end_at=event.get("end_at"),
                members_only=event.get("members_only"),
            )
            new_event.save()

    return HttpResponse(status=201)

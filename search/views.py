from django.db.models import Count, Q
from django.shortcuts import HttpResponse, render

from accounts.models import CustomUser
from posts.models import Post

from .compiler import SearchCompiler


def operator_to_suffix(operator):
    match (operator):
        case "=":
            return ""
        case ">":
            return "__gt"
        case "<":
            return "__lt"


def search_posts(search_query):
    post_qs = Post.objects
    post_qs = post_qs.filter(title__icontains=search_query.search_str)

    filters = {}

    for key, value in search_query.conditions.items():
        operator = value[0]
        operand = value[1]
        print(key, operator, operand)

        match (key):
            case "likes":
                post_qs = post_qs.annotate(
                    likes_count=Count("interactions", filters=Q(interaction="like"))
                )

                filters["likes_count" + operator_to_suffix(operator)] = operand.value
                print(operand.value)
            case "comments":
                post_qs = post_qs.annotate(comments_count=Count("comments"))

                filters["comments_count" + operator_to_suffix(operator)] = operand.value
                print(operand.value)
            case "reposts":
                post_qs = post_qs.annotate(reposts_count=Count("reposts"))

                filters["reposts_count" + operator_to_suffix(operator)] = operand.value
                print(operand.value)
            case "user":
                users = operand.value.split(";")
                q = Q(user__username=users.pop())
                for user in users:
                    q = q | Q(user__username=user)

                post_qs = post_qs.filter(q)
            case "community":
                communities = operand.value.split(";")
                q = Q(community__id=communities.pop())
                for community in communities:
                    q = q | Q(community__id=community)

                post_qs = post_qs.filter(q)

    post_qs = post_qs.filter(**filters)
    return post_qs.all()


def search_users(search_query):
    user_qs = CustomUser.objects
    user_qs = user_qs.filter(username__icontains=search_query.search_str)

    filters = {}

    for key, value in search_query.conditions.items():
        operator = value[0]
        operand = value[1]
        print(key, operator, operand)

        match (key):
            case "follower-count":
                user_qs = user_qs.annotate(follower_count=Count("followers"))
                filters["follower_count" + operator_to_suffix(operator)] = operand.value
            case "following-count":
                user_qs = user_qs.annotate(following_count=Count("following"))
                filters["following_count" + operator_to_suffix(operator)] = (
                    operand.value
                )

    user_qs = user_qs.filter(**filters)
    return user_qs.all()


def create_search_context(search_query):
    ctx = {"posts": [], "users": []}

    types = search_query.conditions["type"][1].value.split(";")
    print(types)

    if "posts" in types:
        ctx["posts"] = search_posts(search_query)
    if "users" in types:
        ctx["users"] = search_users(search_query)

    return ctx


def index_view(request):
    search_str = request.GET.get("q", "")

    print("Raw search string: ", search_str)
    search_query = SearchCompiler(search_str).compile()

    ctx = create_search_context(search_query)

    return HttpResponse(ctx["users"], status=200)

from django.db.models import Count, Q, QuerySet

from communities.models import Communities

from .compiler import SearchCompiler, SearchQuery


def filter_by_key(qs: QuerySet, key: str, value) -> QuerySet:
    obj = {}
    obj[key] = value
    return qs.filter(**obj)


def create_dynamic_query(key: str, value) -> Q:
    obj = {}
    obj[key] = value
    return Q(**obj)


def filter_with_operand(qs: QuerySet, key: str, operand_arr) -> QuerySet:
    obj = {}
    match (operand_arr[0]):
        case "=":
            pass
        case "<":
            key += "__lt"
        case ">":
            key += "__gt"

    return filter_by_key(qs, key, operand_arr[1].value)


def filter_with_eq_list(qs: QuerySet, key: str, operand_arr) -> QuerySet:
    operand = operand_arr[1]
    parts = operand.value.split(";")
    print(parts)

    q = create_dynamic_query(key, parts.pop())
    for part in parts:
        q = q | create_dynamic_query(key, part)

    qs = qs.filter(q)
    return qs


def compile_query(query_str: str) -> SearchQuery:
    search_query = SearchCompiler(query_str).compile()
    print("Raw search string: ", query_str)
    return search_query


def search_communities(qs: QuerySet, q: SearchQuery) -> QuerySet:
    qs = qs.filter(name__icontains=q.search_str)

    if "members" in q.conditions:
        qs = qs.annotate(member_count=Count("members"))
        qs = filter_with_operand(qs, "member_count", q.conditions["members"])

    if "member" in q.conditions:
        qs = qs.filter(members__username=q.conditions["member"][1].value)

    return qs


def search_accounts(qs: QuerySet, q: SearchQuery) -> QuerySet:
    qs = qs.filter(username__icontains=q.search_str)

    return qs


def search_posts(qs: QuerySet, q: SearchQuery) -> QuerySet:
    qs = qs.filter(title__icontains=q.search_str)

    if "likes" in q.conditions:
        qs = qs.annotate(
            like_count=Count("interactions", filters=Q(interaction="like"))
        )
        qs = filter_with_operand(qs, "like_count", q.conditions["likes"])

    if "comments" in q.conditions:
        qs = qs.annotate(comment_count=Count("comments"))
        qs = filter_with_operand(qs, "comment_count", q.conditions["comments"])

    if "reposts" in q.conditions:
        qs = qs.annotate(repost_count=Count("reposts"))
        qs = filter_with_operand(qs, "repost_count", q.conditions["reposts"])

    if "user" in q.conditions:
        qs = filter_with_eq_list(qs, "user__username", q.conditions["user"])

    if "community" in q.conditions:
        qs = filter_with_eq_list(qs, "community__id", q.conditions["community"])

    return qs


def handle_search(query_str: str):
    search_query = SearchCompiler(query_str).compile()

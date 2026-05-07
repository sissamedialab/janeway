def wjs_filter_children_articles(queryset: QuerySet[Article]) -> QuerySet[Article]:
    # Hide "children" articles, because the template shows the children inside the parent
    return queryset.exclude(ancestors__isnull=False)


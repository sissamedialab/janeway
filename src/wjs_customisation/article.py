from django.db.models import QuerySet, Q
from submission.models import Article

def wjs_filter_children_articles(queryset: QuerySet[Article]) -> QuerySet[Article]:
    """
    Filter articles to exclude "children" articles unless in specific sections.

    This function alters the provided queryset by excluding "children" articles (those
    with non-null ancestors) unless they belong to sections explicitly listed as
    allowed (e.g., "Erratum" or "Addendum"). The purpose is to ensure that children
    articles are not displayed separately, as they are already shown within their
    parent article in the template.

    :param queryset: A queryset of articles from which children articles should be filtered.
    :type queryset: QuerySet[Article]
    :return: A queryset excluding children articles unless in allowed sections.
    :rtype: QuerySet[Article]
    """
    allowed_sections_with_children = ["Erratum", "Addendum"]
    exclusions = Q(ancestors__isnull=False)
    for section in allowed_sections_with_children:
        exclusions &= ~Q(section__name=section)
    return queryset.exclude(exclusions)


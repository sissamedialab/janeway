from django.db.models import QuerySet, Q
from submission.models import Article


def wjs_filter_children_articles(
    queryset: QuerySet[Article],
) -> QuerySet[Article]:
    """
    Filter articles to exclude "children" articles unless in specific sections.

    This function alters the provided queryset by excluding articles
    linked to other articles with certain relationships.

    Children "Commentaries" are excluded, because they will appeear in
    the description of their parent.

    :param queryset: A queryset of articles from which
                     children articles should be filtered.
    :type queryset: QuerySet[Article]
    :return: A queryset excluding children articles unless in allowed sections.
    :rtype: QuerySet[Article]
    """
    # Nothing to filter out if the Hydra plugin is not available
    try:
        from plugins.hydra.models import LinkType
    except ImportError:
        return queryset

    relationships_to_hide = {LinkType.COMMENTARY}
    exclusions = Q(linked_to__relationship__in=relationships_to_hide)
    return queryset.exclude(exclusions)

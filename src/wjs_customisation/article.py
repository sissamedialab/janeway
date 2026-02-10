def wjs_filter_children_articles(issue_articles):
    # Hide "children" articles, because the template shows the children inside the parent
    return issue_articles.exclude(ancestors__isnull=False)


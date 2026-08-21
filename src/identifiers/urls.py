__copyright__ = "Copyright 2017 Birkbeck, University of London"
__author__ = "Martin Paul Eve & Andy Byers"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck Centre for Technology and Publishing"
from django.urls import path

from identifiers import views

urlpatterns = [
    path("pingback", views.pingback, name="crossref_pingback"),
    path("<int:article_id>/", views.article_identifiers, name="article_identifiers"),
    path("<int:article_id>/", views.article_identifiers, name="edit_identifiers"),
    path(
        "<int:article_id>/new/",
        views.manage_identifier,
        name="add_new_identifier",
    ),
    path(
        "<int:article_id>/edit/<int:identifier_id>/",
        views.manage_identifier,
        name="edit_identifier",
    ),
    path(
        "<int:article_id>/delete/<int:identifier_id>/",
        views.delete_identifier,
        name="delete_identifier",
    ),
    path(
        "<int:article_id>/issue/<int:identifier_id>/",
        views.issue_doi,
        name="issue_doi",
    ),
    path(
        "<int:article_id>/show/<int:identifier_id>/",
        views.show_doi,
        name="show_doi",
    ),
    path(
        "<int:article_id>/poll/<int:identifier_id>/",
        views.poll_doi,
        name="poll_doi",
    ),
    path(
        "<int:article_id>/poll/output/<int:identifier_id>/",
        views.poll_doi_output,
        name="poll_doi_output",
    ),
    # DOI Manager
    path(
        "doi_manager/",
        views.IdentifierManager.as_view(),
        name="journal_identifier_manager",
    ),
]

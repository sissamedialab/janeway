"""
Fixed, locale-independent date/time formats for this language.

Django 5.0 removed USE_L10N (it is now always effectively True), which means
DateInput/DateTimeInput/TimeInput widgets render and parse using the active
locale's own format lists instead of a project-wide fixed one. Several of
Janeway's configured LANGUAGES do not list ISO 8601 first in their bundled
DATE_INPUT_FORMATS -- and HTML5 <input type="date">/"time"/"datetime-local">
widgets require an exact ISO value or the browser silently discards it, making
the field appear empty regardless of what value the view/form computed.

This module restores ISO-first input formats (matching this project's pre-5.2
behavior under USE_L10N=False) via FORMAT_MODULE_PATH, and keeps DATETIME_FORMAT
in sync with the explicit, non-localized value janeway_global_settings.py
already declares for the same reason.

See core/tests/test_settings.py::TestDateInputFormat for the regression test,
and docs/superpowers/plans/2026-08-21-sissa-r-v1.8-django-5.2-migration-HANDOVER.md
for the original, deliberately-deferred decision this resolves.
"""

DATE_INPUT_FORMATS = [
    "%Y-%m-%d",  # 2006-10-25
]

DATETIME_INPUT_FORMATS = [
    "%Y-%m-%d %H:%M:%S",  # 2006-10-25 14:30:59
    "%Y-%m-%dT%H:%M",  # 2006-10-25T14:30 (HTML5 datetime-local)
    "%Y-%m-%d %H:%M",  # 2006-10-25 14:30
]

TIME_INPUT_FORMATS = [
    "%H:%M:%S",  # 14:30:59
    "%H:%M",  # 14:30
]

DATETIME_FORMAT = "Y-m-d H:i"


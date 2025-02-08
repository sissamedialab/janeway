#!/usr/bin/env bash

if [[ $# -lt 1 ]]; then
    echo -e "Missing parameter\nCommand: $0 /path/to/python"
    exit 1
fi

PYTHON=$1

$PYTHON manage.py link_plugins
$PYTHON manage.py install_themes

$PYTHON manage.py migrate
$PYTHON manage.py build_assets
$PYTHON manage.py collectstatic --noinput

$PYTHON manage.py add_coauthors_submission_email_settings
$PYTHON manage.py add_generic_analytics_code_setting
$PYTHON manage.py add_publication_alert_settings
$PYTHON manage.py add_user_as_main_author_setting

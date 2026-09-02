#!/bin/sh
set -e

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec gunicorn osm_backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120
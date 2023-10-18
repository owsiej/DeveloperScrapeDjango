#!/bin/bash

# Apply database migrations
#if [ "$DATABASE" = "postgres" ]
#then
#    echo "Waiting for postgres..."
#
#    while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
#      sleep 0.1
#    done
#
#    echo "PostgreSQL started"
#fi
python manage.py collectstatic --noinput --clear

echo "Starting ssh"
set -e
service ssh start


echo "Starting ssh"
set -e
service ssh start

# Start server
echo "Starting server"
gunicorn -c ./gunicorn_config.py

exec "$@"
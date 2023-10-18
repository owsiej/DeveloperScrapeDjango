#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

echo "Starting ssh"
set -e
service ssh start

# Start server
echo "Starting server"
python ./manage.py runserver 0.0.0.0:8000

exec "$@"
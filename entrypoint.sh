#!/bin/sh

# Apply database migrations
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi


# Start server
echo "Starting server"
gunicorn -c ./gunicorn_config.py

exec "$@"
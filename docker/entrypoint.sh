#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Function to check if Postgres is ready
postgres_ready() {
    python << END
import sys
import psycopg2
import os

try:
    conn = psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "greenbridge"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
    )
except psycopg2.OperationalError:
    sys.exit(1)
sys.exit(0)
END
}

# Wait for PostgreSQL to be ready
until postgres_ready; do
  echo >&2 "Waiting for PostgreSQL to become available..."
  sleep 1
done
echo >&2 "PostgreSQL is available"

# Apply database migrations
echo >&2 "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo >&2 "Collecting static files..."
python manage.py collectstatic --noinput

# Start Prometheus metrics exporter if enabled
if [ "${PROMETHEUS_EXPORT:-False}" = "True" ]; then
    echo >&2 "Starting Prometheus metrics exporter..."
    python manage.py runserver_plus --nopin 0.0.0.0:8001 &
fi

# Create superuser if needed
echo >&2 "Creating superuser if not exists..."
python manage.py createsuperuser_if_not_exists

# Execute the command passed to the entrypoint
exec "$@" 
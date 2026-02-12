#!/bin/sh

# Stop script if any command fails
set -e

echo "🔄 Applying database migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Execute the passed command
exec "$@"

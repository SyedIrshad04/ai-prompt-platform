#!/bin/sh
set -e

echo "⏳ Waiting for PostgreSQL..."
until python -c "
import psycopg2, os, sys, urllib.parse as up
db_url = os.getenv('DATABASE_URL')
try:
    if db_url:
        psycopg2.connect(db_url)
    else:
        psycopg2.connect(
            dbname=os.getenv('DB_NAME','promptdb'),
            user=os.getenv('DB_USER','promptuser'),
            password=os.getenv('DB_PASSWORD','promptpass'),
            host=os.getenv('DB_HOST','db'),
            port=os.getenv('DB_PORT','5432'),
        )
    sys.exit(0)
except:
    sys.exit(1)
"; do
  echo "  PostgreSQL not ready — sleeping 2s"
  sleep 2
done
echo "✅ PostgreSQL is ready"

echo "⏳ Waiting for Redis..."
until python -c "
import redis, os, sys
try:
    r = redis.from_url(os.getenv('REDIS_URL','redis://redis:6379/0'))
    r.ping()
    sys.exit(0)
except:
    sys.exit(1)
"; do
  echo "  Redis not ready — sleeping 2s"
  sleep 2
done
echo "✅ Redis is ready"

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "🌱 Loading seed data (if any)..."
python manage.py loaddata seed.json 2>/dev/null || true

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 3 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -

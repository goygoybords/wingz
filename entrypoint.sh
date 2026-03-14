#!/bin/sh

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "✅ PostgreSQL is available!"

# Apply migrations
echo "🚀 Running migrations..."
python manage.py migrate

# Seed user types
echo "🌱 Seeding user types..."
python manage.py seed_usertypes

# Seed admin user
echo "👤 Seeding admin user..."
python manage.py seed_admin_user

# Run the development server
echo "🎯 Starting Django development server..."
python manage.py runserver 0.0.0.0:8000

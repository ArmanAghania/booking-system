#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Booking System Docker Container..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
while ! python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1; do
    echo "Database is unavailable - sleeping"
    sleep 1
done

echo "✅ Database is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👑 Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@bookingsystem.com',
        password='admin123',
        first_name='System',
        last_name='Administrator',
        user_type='admin',
        is_verified=True
    )
    print("✅ Superuser 'admin' created with password 'admin123'")
else:
    print("ℹ️  Superuser 'admin' already exists")
EOF

# Create sample data
echo "📊 Creating comprehensive sample data..."
python manage.py create_sample_data

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🎉 Booking System is ready!"
echo "🌐 Access the application at: http://localhost:8000"
echo "👑 Admin login: admin/admin123"

# Execute the main command
exec "$@"

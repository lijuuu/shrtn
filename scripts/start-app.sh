#!/bin/bash

# Start the Django application with proper setup

echo "🚀 Starting Hirethon Template Application..."

# Wait for databases to be ready
echo "⏳ Waiting for databases..."
./scripts/wait-for-db.sh

# Set up the application
echo "🔧 Setting up application..."
python manage.py setup_all

# Start the Django server
echo "🌟 Starting Django server..."
python manage.py runserver 0.0.0.0:8000

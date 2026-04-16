#!/bin/bash
set -e

echo "==================================="
echo "Starting Docker Compose Services..."
echo "==================================="

echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for database to be ready..."
sleep 5

echo ""
echo "Running migrations..."
docker-compose exec -T web python manage.py migrate

echo ""
echo "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo ""
echo "==================================="
echo "✅ All services started successfully!"
echo "==================================="
echo ""
echo "Services running:"
echo "  • Django API: http://localhost:8000"
echo "  • Admin Panel: http://localhost:8000/admin"
echo "  • PostgreSQL: localhost:5432"
echo "  • Redis: localhost:6379"
echo ""
echo "View logs:"
echo "  • All: docker-compose logs -f"
echo "  • Web: docker-compose logs -f web"
echo "  • Worker: docker-compose logs -f celery_worker"
echo "  • Beat: docker-compose logs -f celery_beat"
echo ""
echo "To stop: docker-compose down"

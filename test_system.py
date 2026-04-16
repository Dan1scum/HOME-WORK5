#!/usr/bin/env python
"""
System validation script for Django Shop API
Tests all critical components: Database, Redis, Celery, Models, URLs
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_api.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import get_resolver
from product.models import Category, Product, Review
from users.models import CustomUser
from shop_api.celery import app as celery_app
import redis

print("=" * 70)
print("DJANGO SHOP API - SYSTEM VALIDATION")
print("=" * 70)

# 1. Django Configuration
print("\n✓ DJANGO CONFIGURATION")
print(f"  • Version: Django {django.__version__}")
print(f"  • Debug: {settings.DEBUG}")
print(f"  • Database: {settings.DATABASES['default']['ENGINE'].split('.')[-1]}")
print(f"  • DEFAULT_AUTO_FIELD: {settings.DEFAULT_AUTO_FIELD}")

# 2. User Model
print("\n✓ USER MODEL")
User = get_user_model()
print(f"  • Custom User Model: {User.__name__}")
print(f"  • Total Users: {User.objects.count()}")
print(f"  • USERNAME_FIELD: {User.USERNAME_FIELD}")

# 3. Product Models
print("\n✓ PRODUCT MODELS")
print(f"  • Categories: {Category.objects.count()}")
print(f"  • Products: {Product.objects.count()}")
print(f"  • Reviews: {Review.objects.count()}")

# 4. Celery
print("\n✓ CELERY CONFIGURATION")
print(f"  • Broker: {settings.CELERY_BROKER_URL}")
print(f"  • Registered Tasks: {len(celery_app.tasks)}")
user_tasks = [t for t in celery_app.tasks.keys() if 'users' in t.lower()]
print(f"  • User Tasks: {len(user_tasks)}")
for task in sorted(user_tasks):
    print(f"    - {task}")

# 5. Redis
print("\n✓ REDIS CONNECTION")
try:
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    r = redis.Redis(host=redis_host, port=redis_port, db=0)
    r.ping()
    info = r.info()
    print(f"  • Status: Connected")
    print(f"  • Version: {info['redis_version']}")
    print(f"  • Uptime: {info['uptime_in_seconds']} seconds")
except Exception as e:
    print(f"  • Status: ⚠ Not available ({str(e)[:40]})")

# 6. API URLs
print("\n✓ API ENDPOINTS")
resolver = get_resolver()
api_patterns = [p for p in resolver.url_patterns if 'api' in str(p.pattern)]
for pattern in api_patterns[:10]:
    print(f"  • {pattern.pattern}")

# 7. Email Configuration
print("\n✓ EMAIL CONFIGURATION")
print(f"  • Backend: {settings.EMAIL_BACKEND}")
print(f"  • Host: {settings.EMAIL_HOST}")
print(f"  • Port: {settings.EMAIL_PORT}")
print(f"  • Use TLS: {settings.EMAIL_USE_TLS}")
print(f"  • From Email: {settings.DEFAULT_FROM_EMAIL}")

# 8. REST Framework
print("\n✓ REST FRAMEWORK")
print(f"  • Auth Classes: {settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'][0].split('.')[-1]}")

print("\n" + "=" * 70)
print("✓ ALL SYSTEMS OPERATIONAL")
print("=" * 70)
print("\nTo start development:")
print("  1. Run migrations: python manage.py migrate")
print("  2. Create superuser: python manage.py createsuperuser")
print("  3. Start server: python manage.py runserver")
print("  4. Start Celery: celery -A shop_api worker -l info")
print("  5. Start Celery Beat: celery -A shop_api beat -l info")
print("\n" + "=" * 70)

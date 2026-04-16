#!/usr/bin/env python
"""
API Testing Script
Tests critical endpoints without running server
"""

import os
import sys
import django
import json
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_api.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
client = Client()

print("=" * 70)
print("API ENDPOINT TESTS")
print("=" * 70)

# Test 1: Admin endpoint access
print("\n1. Testing Admin Endpoint")
try:
    response = client.get('/admin/')
    print(f"   • Status: {response.status_code} (expects 302 redirect for login)")
    assert response.status_code in [200, 302], f"Unexpected status {response.status_code}"
    print("   ✓ Admin endpoint accessible")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Product list (no auth required)
print("\n2. Testing Product List API")
try:
    response = client.get('/api/v1/product/')
    print(f"   • Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   • Response contains: {list(data.keys())}")
        print("   ✓ Product list endpoint working")
    else:
        print(f"   ✗ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: User registration endpoint
print("\n3. Testing User Registration Endpoint")
try:
    response = client.post('/api/v1/users/register/', 
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }),
        content_type='application/json'
    )
    print(f"   • Status: {response.status_code}")
    if response.status_code in [200, 201, 400]:  # 400 if user exists
        print("   ✓ Registration endpoint reachable")
    else:
        print(f"   • Response: {response.json() if response.content else 'No content'}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Auth endpoint
print("\n4. Testing User Auth Endpoint")
try:
    response = client.post('/api/v1/users/auth/',
        data=json.dumps({
            'email': 'admin@example.com',
            'password': 'wrongpassword'
        }),
        content_type='application/json'
    )
    print(f"   • Status: {response.status_code}")
    if response.status_code in [200, 401, 400]:
        print("   ✓ Auth endpoint reachable")
    else:
        print(f"   ✗ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Token refresh endpoint
print("\n5. Testing Token Refresh Endpoint")
try:
    response = client.post('/api/v1/token/refresh/',
        data=json.dumps({
            'refresh': 'invalid_token'
        }),
        content_type='application/json'
    )
    print(f"   • Status: {response.status_code}")
    if response.status_code in [200, 401, 400]:
        print("   ✓ Token refresh endpoint reachable")
    else:
        print(f"   ✗ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 70)
print("✓ API TESTS COMPLETE")
print("=" * 70)
print("\nNote: This test uses Client() which doesn't start the server.")
print("For full testing, start the server with: python manage.py runserver")
print("\n" + "=" * 70)

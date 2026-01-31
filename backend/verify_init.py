#!/usr/bin/env python
"""Test script to verify the Flask app and auth service initialization"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("ENVIRONMENT VARIABLES CHECK")
print("=" * 60)
print(f"MONGODB_URI: {os.getenv('MONGODB_URI', 'NOT SET')}")
print(f"MONGODB_DATABASE: {os.getenv('MONGODB_DATABASE', 'NOT SET')}")
print(f"JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY', 'NOT SET')}")
print()

print("=" * 60)
print("IMPORTING APP")
print("=" * 60)
try:
    from app import auth_service
    print(f"✅ Auth Service Status: {auth_service}")
    if auth_service:
        print("✅ Auth service is properly initialized")
    else:
        print("❌ Auth service is None - initialization failed!")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    import traceback
    traceback.print_exc()

"""
Supabase Database Configuration
"""

from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

# Supabase credentials
SUPABASE_URL = "https://guatuutpamzswtbgogqv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1YXR1dXRwYW16c3d0YmdvZ3F2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYxMTc2ODksImV4cCI6MjA4MTY5MzY4OX0.xlVmqtOq3QpGFc9Qe5qLSmShW_e2lJXI8H3Dn6Qn65M"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_supabase():
    """Get Supabase client instance"""
    return supabase

def test_connection():
    """Test Supabase connection"""
    try:
        # Try to fetch from any table to verify connection
        response = supabase.table('teachers').select('*').limit(1).execute()
        print("✓ Supabase connection successful!")
        return True
    except Exception as e:
        print(f"✗ Supabase connection failed: {str(e)}")
        return False

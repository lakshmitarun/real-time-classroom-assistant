#!/usr/bin/env python3
"""
Check MongoDB student data and fix password format
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt

load_dotenv()

# Connect to MongoDB
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'classroomassisstant')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
student_collection = db['student']

print("=" * 60)
print("CHECKING MONGODB STUDENT DATA")
print("=" * 60)

# Get all students
students = list(student_collection.find())
print(f"\n📊 Total students in database: {len(students)}\n")

if students:
    print("Student Records:")
    print("-" * 60)
    for i, student in enumerate(students, 1):
        print(f"\n{i}. User ID: {student.get('user_id', 'N/A')}")
        print(f"   Name: {student.get('name', 'N/A')}")
        print(f"   Password field: {list(student.keys())}")
        print(f"   Has 'password': {'password' in student}")
        print(f"   Has 'password_hash': {'password_hash' in student}")
        
        # Show password value (first 20 chars)
        if 'password' in student:
            pwd = student['password']
            print(f"   Password value: {str(pwd)[:50]}...")
        if 'password_hash' in student:
            pwd_hash = student['password_hash']
            print(f"   Password hash: {str(pwd_hash)[:50]}...")

print("\n" + "=" * 60)
print("SAMPLE TEST CREDENTIALS")
print("=" * 60)

# Try to login with the first student (using plain password)
if students:
    first_student = students[0]
    user_id = first_student.get('user_id')
    
    # Check what password format is stored
    if 'password' in first_student:
        # Plain text password
        plain_password = first_student['password']
        print(f"\n✅ Student found with PLAIN TEXT password!")
        print(f"   User ID: {user_id}")
        print(f"   Password (plain): {plain_password}")
        print(f"\nTry logging in with:")
        print(f"   User ID: {user_id}")
        print(f"   Password: {plain_password}")
    elif 'password_hash' in first_student:
        print(f"\n✅ Student found with HASHED password!")
        print(f"   User ID: {user_id}")
        print(f"   Password (hashed): {first_student['password_hash'][:50]}...")
        print(f"\nCannot display plain password - it's hashed")

print("\n" + "=" * 60)

#!/usr/bin/env python3
"""
Check all students in MongoDB database
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('MONGODB_DATABASE', 'classroomassisstant')

print("=" * 60)
print("📚 CLASSROOM ASSISTANT - STUDENT DATABASE CHECK")
print("=" * 60)

try:
    client = MongoClient(MONGODB_URI)
    client.admin.command('ping')
    print(f"✅ Connected to MongoDB")
    print(f"   URI: {MONGODB_URI}")
    print(f"   Database: {DATABASE_NAME}")
    
    db = client[DATABASE_NAME]
    student_collection = db['student']
    
    # Count total students
    total_students = student_collection.count_documents({})
    print(f"\n📊 Total Students: {total_students}")
    
    if total_students == 0:
        print("⚠️  No students found in database!")
    else:
        print("\n" + "=" * 60)
        print("STUDENT LIST:")
        print("=" * 60)
        
        # Fetch all students
        students = student_collection.find({}).sort('_id', -1)
        
        for i, student in enumerate(students, 1):
            print(f"\n{i}. Student Record:")
            print(f"   User ID: {student.get('user_id', 'N/A')}")
            print(f"   Name: {student.get('name', 'N/A')}")
            print(f"   Email: {student.get('email', 'N/A')}")
            print(f"   Roll Number: {student.get('roll_number', 'N/A')}")
            print(f"   Class: {student.get('class', 'N/A')}")
            print(f"   Created: {student.get('created_at', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✅ Check completed successfully!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nMake sure:")
    print("  1. MongoDB is running locally")
    print("  2. Connection string is correct")
    print("  3. Database name matches")

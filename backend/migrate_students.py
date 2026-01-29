#!/usr/bin/env python3
"""
Migration script: Import student data from CSV to MongoDB
Reads from data/student_logins.csv and imports to MongoDB 'student' collection
"""

import csv
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt

# Load environment variables
load_dotenv()

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def migrate_students():
    """Migrate student data from CSV to MongoDB"""
    
    # MongoDB configuration
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    database_name = os.getenv('MONGODB_DATABASE', 'classroomassisstant')
    
    print(f"Connecting to MongoDB: {mongo_uri}")
    print(f"Database: {database_name}")
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        db = client[database_name]
        student_collection = db['student']
        
        # Create index
        student_collection.create_index('user_id', unique=True)
        
        print("[OK] Connected to MongoDB")
        
        # CSV file path
        csv_path = Path(__file__).parent.parent / 'data' / 'student_logins.csv'
        
        if not csv_path.exists():
            print(f"[ERROR] CSV file not found: {csv_path}")
            return False
        
        print(f"[OK] Reading CSV: {csv_path}")
        
        # Count existing students
        existing_count = student_collection.count_documents({})
        print(f"[INFO] Existing students in MongoDB: {existing_count}")
        
        # Read and import from CSV
        imported = 0
        skipped = 0
        errors = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    user_id = row.get('user_id', '').strip()
                    name = row.get('name', '').strip()
                    password = row.get('password', '').strip()
                    role = row.get('role', 'student').strip()
                    preferred_language = row.get('preferred_language', '').strip()
                    
                    if not user_id or not password:
                        print(f"[SKIP] Missing user_id or password: {user_id}")
                        skipped += 1
                        continue
                    
                    # Check if student already exists
                    existing = student_collection.find_one({'user_id': user_id})
                    if existing:
                        print(f"[SKIP] Student already exists: {user_id}")
                        skipped += 1
                        continue
                    
                    # Create student document
                    student = {
                        'user_id': user_id,
                        'name': name,
                        'password_hash': hash_password(password),
                        'role': role,
                        'preferred_language': preferred_language,
                        'created_at': None,
                        'last_login': None
                    }
                    
                    # Insert into MongoDB
                    result = student_collection.insert_one(student)
                    imported += 1
                    
                    if imported % 10 == 0:
                        print(f"[INFO] Imported {imported} students...")
                
                except Exception as e:
                    print(f"[ERROR] Failed to import student {user_id}: {str(e)}")
                    errors += 1
                    continue
        
        print(f"\n=== Migration Summary ===")
        print(f"Imported: {imported}")
        print(f"Skipped: {skipped}")
        print(f"Errors: {errors}")
        print(f"Total in collection: {student_collection.count_documents({})}")
        
        client.close()
        print("[OK] Migration completed successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_students()
    sys.exit(0 if success else 1)

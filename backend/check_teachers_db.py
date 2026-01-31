from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client[os.getenv('MONGODB_DATABASE', 'classroomassisstant')]
teachers = db['teachersignup'].find()
print("Teachers in database:")
for t in teachers:
    print(f"  Email: {t.get('email')}, Name: {t.get('name')}, Password: {t.get('password')}")

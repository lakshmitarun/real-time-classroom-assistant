# Fix: Demo Teacher (Fallback) Issue

## Problem
When logging in on Vercel deployment, you see "Welcome, Demo Teacher (Fallback)" instead of your real teacher name.

## Root Cause
The backend's `AuthServiceMongoDB` fails to initialize because the `MONGODB_URI` environment variable is not set on Vercel.

## Solution
Set the MongoDB environment variables on your Vercel backend deployment:

### Step 1: Get Your MongoDB URI
From your local `.env` file, find the value of `MONGODB_URI`. It should look like:
```
mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### Step 2: Add to Vercel
Go to your Vercel project → Settings → Environment Variables and add:

```
MONGODB_URI = [your-mongodb-uri-from-.env]
MONGODB_DATABASE = classroomassisstant
JWT_SECRET_KEY = jwt-classroom-assistant-2024
```

### Step 3: Redeploy
After adding environment variables:
1. Go to Deployments
2. Redeploy the production version OR
3. Push a new commit to trigger auto-deploy

## Verification
After redeployment:
1. Go to https://classroom-assistant-backend.vercel.app
2. Check the logs to see if AuthServiceMongoDB initialized successfully
3. Try logging in - you should see your real teacher name

## Local Testing
Your local setup is working correctly! When you run the backend locally (`python app.py`), you can test with:
- Email: `lakshmitaruntarun@gmail.com`
- Password: `tarun123`
- Expected name: `PALIVELA LAKSHMI TARUN`

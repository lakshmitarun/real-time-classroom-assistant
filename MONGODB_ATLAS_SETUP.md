# MongoDB Atlas Setup Guide

## Step 1: Create MongoDB Atlas Account

1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Create FREE account
3. Verify email

## Step 2: Create a Cluster

1. Click **Create** button
2. Choose **Shared** (Free tier)
3. Select region closest to you
4. Click **Create Cluster** (wait ~3-5 minutes)

## Step 3: Add Database User

1. In left sidebar, click **Database Access**
2. Click **Add New Database User**
3. Enter:
   - **Username:** `classroom`
   - **Password:** (generate secure password, SAVE IT!)
4. Click **Add User**

## Step 4: Allow Network Access

1. In left sidebar, click **Network Access**
2. Click **Add IP Address**
3. Select **Allow access from anywhere** (for Vercel)
4. Click **Confirm**

## Step 5: Get Connection String

1. Click **Databases** in left sidebar
2. Click **Connect** button on your cluster
3. Select **Drivers** → **Node.js**
4. Copy the connection string

**It will look like:**
```
mongodb+srv://classroom:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**Replace PASSWORD with your actual password!**

## Step 6: Update Files

Replace these in files:

### `backend/.env`
```
MONGODB_URI=mongodb+srv://classroom:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=classroomassisstant
```

### Vercel Dashboard - Backend Project
**Settings** → **Environment Variables**:

- `MONGODB_URI` = `mongodb+srv://classroom:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
- `DATABASE_NAME` = `classroomassisstant`
- `JWT_SECRET` = `jwt-classroom-assistant-2024`
- `GOOGLE_CLIENT_ID` = `562438583684-5r38bmc33jhdnsk18uds1kds7h937dcg.apps.googleusercontent.com`

### Vercel Dashboard - Frontend Project
**Settings** → **Environment Variables**:

- `REACT_APP_API_URL` = `https://classroom-assistant-backend.vercel.app`
- `REACT_APP_GOOGLE_CLIENT_ID` = `562438583684-5r38bmc33jhdnsk18uds1kds7h937dcg.apps.googleusercontent.com`
- `REACT_APP_MOCK_GOOGLE_AUTH` = `false`

## Step 7: Test Locally

```bash
cd backend
python app.py
```

Try login with:
- Roll: `236Q1A4519`
- Password: `236Q1A4519@123`

## Step 8: Redeploy on Vercel

1. Backend: Go to **Deployments** → **Redeploy**
2. Frontend: Go to **Deployments** → **Redeploy**
3. Wait 2-3 minutes

## Step 9: Test on Vercel

Visit: https://real-time-classroom-assistant-ye11.vercel.app

Try login again with same credentials!

---

**If you get connection errors:**
- Check MongoDB Atlas Network Access (should allow 0.0.0.0/0)
- Verify password is correct in connection string
- Check database name is `classroomassisstant`

**If student login fails:**
- Ensure 110 students are in MongoDB `student` collection
- Check passwords are bcrypt hashed
- Verify JWT_SECRET matches

**Done!** 🎉

# Production Deployment Guide - Vercel

This guide provides step-by-step instructions to deploy the Real-Time Classroom Assistant to Vercel with proper CORS and Google OAuth configuration.

## Prerequisites

- GitHub account with the repository pushed
- Vercel account (free tier supported)
- Google Cloud Console project with OAuth 2.0 credentials
- Two Vercel projects: one for frontend, one for backend

---

## Issue Summary

**Problem**: Application works locally but fails in production with:
1. **Google OAuth 403 Error**: "The given origin is not allowed for the given client ID"
2. **CORS Errors**: "No 'Access-Control-Allow-Origin' header"
3. **Preflight Failures**: OPTIONS requests blocked (net::ERR_FAILED, 404)

**Solution**: Configure CORS properly on backend + whitelist frontend origin in Google OAuth

---

## Step 1: Configure Google OAuth

### 1.1 Get Your Frontend URL
- Frontend URL: `https://real-time-classroom-assistant-2ze2pt6u7.vercel.app`
- Backend URL: `https://classroom-assistant-backend.vercel.app`

### 1.2 Update Google Cloud Console

1. Open [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Go to **APIs & Services** → **Credentials**
4. Find and click on your **OAuth 2.0 Client ID** (Web application)
5. Under **Authorized JavaScript origins**, add:
   ```
   https://real-time-classroom-assistant-2ze2pt6u7.vercel.app
   ```
6. Click **Save** (may take 5-10 minutes to propagate)

> **Note**: If you have multiple frontend deployments, add all of them here.

---

## Step 2: Deploy Backend to Vercel

### 2.1 Create Vercel Backend Project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository: `lakshmitarun/Real-Time-Classroom-Assistant`
3. For **Framework**: Select "Other"
4. For **Root Directory**: Select `./backend`
5. Under **Build Command**, enter:
   ```bash
   pip install -r requirements.txt
   ```
6. Under **Start Command**, enter:
   ```bash
   gunicorn app:app
   ```
7. Click **Deploy**

### 2.2 Set Environment Variables in Backend

After deployment, go to **Settings** → **Environment Variables** and add:

| Variable | Value | Notes |
|----------|-------|-------|
| `GOOGLE_CLIENT_ID` | Your OAuth Client ID | From Google Cloud Console |
| `JWT_SECRET_KEY` | Generate random string (32+ chars) | Used for JWT tokens |
| `FLASK_ENV` | `production` | Flask environment |
| `DEBUG` | `False` | Disable debug mode |
| `CORS_ORIGINS` | `https://real-time-classroom-assistant-2ze2pt6u7.vercel.app` | Frontend URL |

**Steps to set variables:**
1. In Vercel project: Go to **Settings** → **Environment Variables**
2. Click **Add New** for each variable
3. Enter **Name** and **Value**
4. Select **Environments**: Check "Production"
5. Click **Save**
6. Vercel will auto-redeploy

### 2.3 Add Gunicorn to Requirements

Update `backend/requirements.txt` to include:
```
gunicorn==21.2.0
```

> **Why**: Vercel needs WSGI server; Flask dev server doesn't work on Vercel

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Frontend Project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import same repository
3. For **Framework**: Select "Create React App"
4. For **Root Directory**: Select `./frontend`
5. For **Build Command**: `npm run build`
6. For **Output Directory**: `build`
7. Click **Deploy**

### 3.2 Set Environment Variables in Frontend

Go to **Settings** → **Environment Variables** and add:

| Variable | Value | Notes |
|----------|-------|-------|
| `REACT_APP_API_URL` | `https://classroom-assistant-backend.vercel.app` | Backend URL |
| `REACT_APP_GOOGLE_CLIENT_ID` | Your OAuth Client ID | From Google Cloud Console |

**Steps:**
1. Go to **Settings** → **Environment Variables**
2. Add each variable with Production environment selected
3. Save
4. Vercel will auto-redeploy

---

## Step 4: Verify Deployment

### 4.1 Test Frontend
1. Open your frontend URL: `https://real-time-classroom-assistant-2ze2pt6u7.vercel.app`
2. Should see the login page without 404 errors
3. Check browser console (F12) for errors

### 4.2 Test Backend Health
```bash
curl https://classroom-assistant-backend.vercel.app/api/health
```
Expected response:
```json
{"status":"ok","message":"Service is healthy","timestamp":"2025-12-20T..."}
```

### 4.3 Test CORS Preflight
```bash
curl -X OPTIONS https://classroom-assistant-backend.vercel.app/api/broadcast \
  -H "Origin: https://real-time-classroom-assistant-2ze2pt6u7.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
```
Look for these headers in response:
```
Access-Control-Allow-Origin: https://real-time-classroom-assistant-2ze2pt6u7.vercel.app
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, Accept
```

### 4.4 Test Google OAuth
1. Click "Sign in with Google" on login page
2. Should NOT see 403 error
3. Should redirect to teacher/student dashboard after login

---

## Step 5: Troubleshooting

### Issue: Still Getting CORS Error

**Solution 1**: Check Environment Variables
- Verify `CORS_ORIGINS` is set correctly in backend Vercel project
- Check `REACT_APP_API_URL` is set in frontend Vercel project
- Trigger redeploy after changing variables

**Solution 2**: Check Backend Logs
1. In Vercel backend project: Go to **Deployments**
2. Click latest deployment
3. Go to **Functions** and check logs for CORS errors

**Solution 3**: Clear Browser Cache
```javascript
// In browser console
localStorage.clear()
sessionStorage.clear()
// Then refresh page
```

### Issue: Google OAuth 403 Error

**Solution 1**: Verify Google Cloud Console
- Double-check authorized origin includes HTTPS
- Wait 5-10 minutes for propagation
- Try in incognito window (fresh cache)

**Solution 2**: Verify Environment Variable
- Backend must have correct `GOOGLE_CLIENT_ID`
- Frontend must have correct `REACT_APP_GOOGLE_CLIENT_ID`
- Should match exactly (case-sensitive)

### Issue: 404 on API Endpoints

**Solution**: Ensure backend is running
```bash
curl https://classroom-assistant-backend.vercel.app/api/health
```
If this returns 404, backend deployment failed. Check:
1. Root Directory is `./backend`
2. Start Command is `gunicorn app:app`
3. Gunicorn is in requirements.txt

---

## Code Changes Made

### Backend (app.py)
- ✅ Added explicit OPTIONS handler for preflight requests
- ✅ Included environment-based CORS origins
- ✅ Support for multiple Vercel deployments

### Frontend (.env.production)
- ✅ Points to production backend URL
- ✅ Google Client ID included

### Configuration Files
- ✅ .env.example - documented all required variables
- ✅ vercel.json - configured build process

---

## Security Notes

1. **Never commit `.env` files** - use Vercel's environment variables
2. **JWT_SECRET_KEY** - generate strong random string:
   ```python
   import secrets
   secrets.token_urlsafe(32)
   ```
3. **GOOGLE_CLIENT_ID** - keep secret in environment variables, never commit
4. **CORS_ORIGINS** - whitelist only your actual frontend URLs

---

## Summary Checklist

- [ ] Added your frontend URL to Google Cloud Console authorized origins
- [ ] Created Vercel backend project with `./backend` root directory
- [ ] Set all backend environment variables in Vercel
- [ ] Created Vercel frontend project with `./frontend` root directory
- [ ] Set all frontend environment variables in Vercel
- [ ] Tested backend health endpoint with curl
- [ ] Tested CORS preflight request
- [ ] Tested Google OAuth login on production
- [ ] Verified student can join class by code
- [ ] Verified teacher can broadcast translations

---

## Support Commands

```bash
# View backend logs (replace PROJECT_ID)
vercel logs classroom-assistant-backend.vercel.app

# View frontend logs
vercel logs real-time-classroom-assistant.vercel.app

# Clear Vercel cache and redeploy
vercel --prod

# Test CORS from command line
curl -X OPTIONS https://your-backend.vercel.app/api/broadcast \
  -H "Origin: https://your-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -i
```

---

## Still Having Issues?

1. Check browser console (F12) for exact error messages
2. Check Vercel deployment logs for backend errors
3. Verify environment variables are spelled correctly
4. Ensure URLs use HTTPS (not HTTP)
5. Check that origins don't have trailing slashes
6. Test from incognito window (fresh cache)


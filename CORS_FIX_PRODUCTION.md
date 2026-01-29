# CORS Fix - Production Deployment Checklist

## Problem
Frontend (https://real-time-classroom-assistant.vercel.app) cannot connect to backend (https://classroom-assistant-backend.vercel.app) due to CORS errors.

## Solution

### Frontend Changes ✅
- Added `REACT_APP_API_URL` to `.env` for local development
- `.env.production` already has correct production URL: `https://classroom-assistant-backend.vercel.app`

### Backend Changes ✅
- Updated CORS to use specific origins list (not wildcard)
- Added support for credentials (`supports_credentials: True`)
- Improved logging with ✅/❌ indicators
- Configured all headers properly

### Required Vercel Dashboard Actions (DO THIS NOW!)

#### For Frontend Project:
1. **Go to** https://vercel.com/dashboard
2. **Select** `real-time-classroom-assistant` project
3. **Go to Settings → Environment Variables**
4. **Add new variable:**
   ```
   Name: REACT_APP_API_URL
   Value: https://classroom-assistant-backend.vercel.app
   Environment: Production
   ```
5. **Click Save**
6. **Redeploy** from Deployments tab

#### For Backend Project:
1. **Go to** https://vercel.com/dashboard
2. **Select** `classroom-assistant-backend` project
3. **Go to Settings → Environment Variables**
4. **Check if these exist, if not add them:**
   ```
   Name: FLASK_ENV
   Value: production
   Environment: Production
   ```
5. **Click Save**
6. **Redeploy** from Deployments tab

## Verification Checklist

After setting environment variables and redeploying, test:

- [ ] Frontend loads at https://real-time-classroom-assistant.vercel.app
- [ ] Open browser DevTools → Network tab
- [ ] Try to login with student ID
- [ ] Check network request:
  - [ ] URL is `https://classroom-assistant-backend.vercel.app/api/student/login`
  - [ ] Request Headers include: `Content-Type: application/json`
  - [ ] Response Headers include: `Access-Control-Allow-Origin: https://real-time-classroom-assistant.vercel.app`
  - [ ] Response Status: `200 OK` (not 4xx or 5xx)
  - [ ] Response body has student data
- [ ] No CORS error in console
- [ ] Login succeeds and redirect works

## CORS Headers Expected

When frontend requests login, backend should respond with:
```
Access-Control-Allow-Origin: https://real-time-classroom-assistant.vercel.app
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, Accept
Access-Control-Max-Age: 3600
```

## Testing Login Flow

1. Go to https://real-time-classroom-assistant.vercel.app/login
2. Enter student ID: `23B21A4558` (example)
3. Click Login
4. Open DevTools (F12) → Console
5. Check for errors:
   - ✅ No CORS errors
   - ✅ API response visible in Network tab
   - ✅ User data received

## If Still Getting CORS Error

Check:
1. ✅ Environment variable `REACT_APP_API_URL` is set in Vercel frontend
2. ✅ Vercel frontend is redeployed (status: "Ready")
3. ✅ Backend CORS allows the frontend domain
4. ✅ Backend is running/deployed
5. ✅ Check Network tab: actual API URL being called
6. ✅ Check Response headers: Access-Control-Allow-Origin present

## Quick Links

- Frontend project: https://vercel.com/dashboard (search: real-time-classroom-assistant)
- Backend project: https://vercel.com/dashboard (search: classroom-assistant-backend)
- Frontend repo: https://github.com/lakshmitarun/real-time-classroom-assistant

Done! Now go set the environment variables in Vercel Dashboard! 🚀

# Vercel Deployment Complete Fix Guide

## Problem Summary

React app deployed to Vercel shows:
- ✅ Deployment status: "Ready"
- ❌ Opening URL returns: `404 NOT_FOUND`
- ❌ Root domain doesn't serve `index.html`

## Root Cause Analysis

React is a Single Page Application (SPA). It needs:
1. One HTML entry point (`index.html`)
2. All routes rewritten to that entry point
3. React Router handles URL matching in the browser

**Without proper config**, Vercel treats each URL as a separate file request and returns 404.

---

## Step-by-Step Fix

### Step 1: Create `frontend/vercel.json`

This file was just created with the following content:

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "react",
  "outputDirectory": "build",
  "env": {
    "REACT_APP_GOOGLE_CLIENT_ID": "@react_app_google_client_id",
    "REACT_APP_API_URL": "@react_app_api_url"
  },
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**What each section does:**

| Setting | Purpose |
|---------|---------|
| `buildCommand` | How Vercel builds your app |
| `framework` | Helps Vercel detect and optimize for React |
| `outputDirectory` | Where built files go (React uses `build/`) |
| `rewrites` | **CRITICAL**: Routes all requests to index.html |
| `env` | Links environment variables |

### Step 2: Verify `package.json` Build Script

✅ Already correct:
```json
"build": "react-scripts build"
```

### Step 3: Create `.vercelignore` (Optional)

Already created. This file prevents Vercel from excluding needed files.

### Step 4: Configure Vercel Dashboard

Go to **Project Settings → General**:

1. **Framework Preset**: Select `React` (should auto-detect)
2. **Build Command**: `npm run build`
3. **Output Directory**: `build`
4. **Install Command**: `npm install`

### Step 5: Set Environment Variables

Go to **Project Settings → Environment Variables**:

Add these variables:
```
REACT_APP_GOOGLE_CLIENT_ID = 562438583684-5r38bmc33jhdnsk18uds1kds7h937dcg.apps.googleusercontent.com
REACT_APP_API_URL = https://your-backend-api.com
REACT_APP_USE_MOCK = false
```

### Step 6: Deploy

Push changes to trigger redeploy:

```bash
cd d:\classroom-assistant
git add -A
git commit -m "fix: Add Vercel configuration for React SPA routing"
git push
```

Monitor deployment in Vercel dashboard.

---

## Verification Checklist

After deployment, verify:

- [ ] **Vercel shows "Ready"** status
- [ ] **Root domain loads** (`https://your-app.vercel.app/`)
- [ ] **Index page displays** (homepage loads)
- [ ] **Navigation works** (React Router routes work)
- [ ] **Sub-pages load** (`/student`, `/teacher`, etc.)
- [ ] **Hard refresh (Ctrl+Shift+R)** doesn't break anything
- [ ] **Console has no errors** (check browser dev tools)
- [ ] **API calls work** (if backend is connected)

---

## How SPA Routing Works on Vercel

```
User Request Flow:
1. User visits: https://your-app.vercel.app/student
2. Vercel receives request for /student
3. vercel.json "rewrites" config redirects to /index.html
4. User receives index.html + React bundle
5. React Router reads URL (/student)
6. React Router renders StudentView component
7. User sees the student page
```

**Without rewrites:**
```
❌ User visits: https://your-app.vercel.app/student
❌ Vercel looks for file: /build/student (doesn't exist)
❌ Returns 404
```

---

## Troubleshooting

### Issue 1: Still Getting 404

**Solution:**
1. Clear Vercel cache: Vercel Dashboard → Settings → Git → Redeploy
2. Check build logs for errors
3. Verify `vercel.json` is in `frontend/` directory
4. Ensure `build/` folder contains `index.html`

### Issue 2: Environment Variables Not Working

**Solution:**
- Add all `REACT_APP_*` variables to Vercel dashboard
- Redeploy after adding variables
- Variables are only available at build time for Create React App

### Issue 3: Sub-routes Work But Styles/Images Break

**Solution:**
- Check your public folder paths
- Ensure images are in `frontend/public/`
- Use absolute paths starting with `/`

### Issue 4: API Calls Return 403/CORS Error

**Solution:**
- Verify backend CORS includes your Vercel domain
- Backend should allow: `https://your-app.vercel.app`
- Check [backend/app.py](../backend/app.py) line 46 has your domain

### Issue 5: Build Fails with Dependencies Error

**Solution:**
```bash
# Local test
cd frontend
npm ci  # Clean install
npm run build  # Test build
```

---

## Files Changed

✅ **Created:**
- `frontend/vercel.json` - Vercel configuration
- `frontend/.vercelignore` - Deployment ignore rules
- `frontend/VERCEL_FIX.md` - This documentation

✅ **Already Correct:**
- `frontend/package.json` - Build script is correct
- `backend/app.py` - CORS already includes Vercel domains

---

## Production Checklist

Before going live:

- [ ] All environment variables set in Vercel
- [ ] Backend API URL configured for production
- [ ] Google OAuth client ID added to environment variables
- [ ] Test deploy to staging first
- [ ] Verify API connectivity in production
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Test all major flows on production domain

---

## References

- [Vercel React Documentation](https://vercel.com/docs/frameworks/react)
- [Vercel Rewrites Documentation](https://vercel.com/docs/edge-network/rewrites-and-redirects)
- [Create React App Deployment](https://create-react-app.dev/docs/deployment/vercel/)


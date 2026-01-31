# Fix Google OAuth 403 Error on Vercel

## Problem
Google OAuth is blocking login attempts from your Vercel frontend with error:
```
[GSI_LOGGER]: The given origin is not allowed for the given client ID.
```

**Status Code:** 403 Forbidden

---

## Root Cause
Your Vercel frontend URL is not whitelisted in Google Cloud Console for your OAuth Client ID.

**Frontend URL:** `https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app`

**Client ID:** `562438583684-5r38bmc33jhdnsk18uds1kds7h937dcg.apps.googleusercontent.com`

---

## Solution: Add ONLY Vercel URL to Google Cloud Console

Since `localhost:3001` is already configured, you only need to add the **Vercel production URLs**.

### Step 1: Access Google Cloud Console

1. Open: https://console.cloud.google.com/
2. Select your project from dropdown
3. Go to **APIs & Services → Credentials**

### Step 2: Find Your OAuth Client

1. Under "OAuth 2.0 Client IDs", click the Web client: `562438583684-5r38bmc33jhdnsk18uds1kds7h937dcg.apps.googleusercontent.com`

### Step 3: ADD ONLY These Vercel URLs

**In "Authorized JavaScript origins" section - ADD:**

```
https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app
```

(localhost:3001 is already there, don't duplicate)

**In "Authorized redirect URIs" section - ADD:**

```
https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app/
```

(Note the trailing `/` - important for redirect URIs!)

### Step 4: Save

Click **Save** button at bottom.

---

## ✅ What Should Look Like After

**Authorized JavaScript origins should have:**
```
http://localhost:3001          ← Already there ✅
https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app  ← Add this
```

**Authorized redirect URIs should have:**
```
http://localhost:3001/         ← Already there ✅
https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app/  ← Add this (with trailing slash)
```

---

---

## Expected Result After Fix

✅ **Before:** 403 Forbidden - "origin not allowed"  
✅ **After:** Google login button works, shows login popup

**Timeline:**
- Changes take effect **immediately** (sometimes within 1-2 minutes)
- Clear browser cache if it still doesn't work
- Hard refresh: **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)

---

## Testing After Fix

### Local Testing
```
1. Visit: http://localhost:3001/
2. Click "Teacher Login" on home page
3. Click "Sign in with Google" button
4. Should see Google login popup (not 403 error)
```

### Vercel Testing
```
1. Visit: https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app
2. Click "Teacher Login"
3. Click "Sign in with Google" button
4. Should see Google login popup (not 403 error)
```

---

## Still Getting 403?

**Try these steps:**

1. **Hard refresh browser:**
   - Windows: Ctrl+Shift+Delete → Select "All time" → Clear data
   - Or: Ctrl+Shift+R for hard refresh

2. **Check DevTools Console (F12):**
   - Should show: `Google Client ID loaded: YES`
   - Should show the client ID (first 20 chars)
   - If NO, the environment variable is not set

3. **Verify URLs are exact:**
   - No trailing spaces
   - No typos
   - HTTPS required for production
   - HTTP allowed for localhost

4. **Check you're in the right project:**
   - Google Cloud Console → top left dropdown
   - Select correct project
   - Make sure OAuth client is in THIS project

5. **Try incognito/private window:**
   - Clears all cache
   - Tests fresh browser state

---

## OAuth Flow

```
User clicks "Sign in with Google"
        ↓
Frontend sends request to: accounts.google.com/gsi/button
        ↓
Google checks request origin against whitelist
        ↓
✅ If URL is in whitelist → Shows login popup
❌ If URL NOT in whitelist → 403 Forbidden
```

---

## Reference

- **Google Cloud Console:** https://console.cloud.google.com/apis/credentials
- **Current Client ID:** `562438583684-5r38bmc33jhdnsk18uds1kds7h937dcg.apps.googleusercontent.com`
- **Frontend URL (Vercel):** `https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app`
- **Frontend URL (Local):** `http://localhost:3001`

---

## Additional Notes

- **Do NOT share** the Client ID publicly
- **Do NOT commit** environment variables with secrets
- Each origin needs to be added separately
- Spaces and special characters matter!
- If you change the OAuth Client ID, update `REACT_APP_GOOGLE_CLIENT_ID` in .env files

---

**Last Updated:** 2026-01-31  
**Status:** Waiting for Google Cloud Console configuration

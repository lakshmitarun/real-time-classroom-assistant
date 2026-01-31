# Deployment Guide: React Frontend + Flask Backend on Vercel

## 📋 Problem Summary

| Issue | Cause | Fix |
|-------|-------|-----|
| "Backend not reachable" on Vercel | Wrong API URL or `withCredentials: true` | Use correct `REACT_APP_API_URL` env var, remove credentials |
| Missing CSS on Vercel | CSS import paths broken | CSS imports work fine with CRA - this is usually a build issue |
| Works locally but fails on Vercel | Different NODE_ENV and API URLs | Environment variables not set in Vercel dashboard |

---

## 🔧 Working Configuration

### 1. Frontend: `src/config/api.js`

```javascript
/**
 * API Configuration for Create React App
 * 
 * Environment Variable Priority:
 * 1. REACT_APP_API_URL (set in .env or .env.production)
 * 2. Default based on NODE_ENV
 * 
 * For Vercel Production:
 *   - Set REACT_APP_API_URL = https://classroom-assistant-backend.vercel.app
 * 
 * For Local Development:
 *   - REACT_APP_API_URL = http://localhost:5000
 */

const getApiUrl = () => {
  // Priority 1: Environment variable
  if (process.env.REACT_APP_API_URL) {
    console.log('✅ Using REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
    return process.env.REACT_APP_API_URL;
  }
  
  // Priority 2: Default based on environment
  if (process.env.NODE_ENV === 'production') {
    console.log('⚠️ Production mode: Using default backend URL');
    return 'https://classroom-assistant-backend.vercel.app';
  }
  
  // Local development
  console.log('✅ Development mode: Using localhost backend');
  return 'http://localhost:5000';
};

const API_BASE_URL = getApiUrl();

console.log('🔧 API Config:');
console.log('  - NODE_ENV:', process.env.NODE_ENV);
console.log('  - API_BASE_URL:', API_BASE_URL);
console.log('  - REACT_APP_API_URL:', process.env.REACT_APP_API_URL || '(not set)');

export default API_BASE_URL;
```

### 2. Frontend: `.env` (Local Development)

```bash
PORT=3001
BROWSER=none
REACT_APP_API_URL=http://localhost:5000
REACT_APP_GOOGLE_CLIENT_ID=562438583684-5r38bmc33jhdnsk18uds1kds7h937dcg.apps.googleusercontent.com
REACT_APP_DEBUG=true
```

### 3. Frontend: `.env.production` (Vercel)

```bash
REACT_APP_API_URL=https://classroom-assistant-backend.vercel.app
REACT_APP_MOCK_GOOGLE_AUTH=false
REACT_APP_DEBUG=false
```

### 4. Frontend: `src/pages/StudentView.js` (Login Axios Call)

```javascript
const handleLogin = async (e) => {
  e.preventDefault();
  setLoginError('');
  console.log('🔐 Login Attempt:');
  console.log('  - API URL:', API_BASE_URL);
  console.log('  - User ID:', loginForm.userId.trim());

  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/student/login`,
      {
        userId: loginForm.userId.trim(),
        password: loginForm.password.trim()
      },
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: 10000 // 10 second timeout
      }
    );

    console.log('✅ Login Success:', response.data);

    if (response.data.success) {
      const userData = response.data.user || response.data;
      setStudentData(userData);
      setIsLoggedIn(true);

      localStorage.setItem('studentSession', JSON.stringify(userData));
      localStorage.setItem('userRole', userData.role || 'student');

      if (userData.preferredLanguage) {
        setSelectedLanguage(userData.preferredLanguage.toLowerCase());
      }
    } else {
      setLoginError('Invalid credentials');
    }
  } catch (error) {
    console.error('❌ Login Error Details:');
    console.error('  - Message:', error.message);
    console.error('  - Status:', error.response?.status);
    console.error('  - Data:', error.response?.data);
    console.error('  - Config URL:', error.config?.url);
    
    if (error.response?.status === 401) {
      setLoginError('Invalid user ID or password');
    } else if (error.response?.status === 404) {
      setLoginError('Backend server not found. Check API URL: ' + API_BASE_URL);
    } else if (error.code === 'ECONNABORTED') {
      setLoginError('Request timeout - backend is slow or unreachable');
    } else if (error.message === 'Network Error') {
      setLoginError('Network error - check if backend is running at: ' + API_BASE_URL);
    } else {
      setLoginError('Backend not reachable. Error: ' + error.message);
    }
  }
};
```

### 5. Root: `vercel.json` (Build Config)

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/build",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## 🚀 Vercel Dashboard Setup

### Step 1: Set Environment Variables

In your Vercel Dashboard:

1. Go to **Settings → Environment Variables**
2. Add these variables:

```
REACT_APP_API_URL = https://classroom-assistant-backend.vercel.app
REACT_APP_DEBUG = false
```

3. Make sure they apply to **Production** environment
4. Save and redeploy

### Step 2: Verify Backend URL

1. Go to [https://classroom-assistant-backend.vercel.app/](https://classroom-assistant-backend.vercel.app/)
2. You should see your Flask backend running
3. If 404, check backend deployment

---

## 🎯 Why It Works Locally But Not on Vercel

| Local Development | Vercel Production |
|---|---|
| `npm start` runs with `.env` | Build uses `.env.production` |
| `NODE_ENV=development` | `NODE_ENV=production` |
| API URL: `http://localhost:5000` | API URL: env variable or default |
| Backend runs on same machine | Backend on different Vercel instance |
| No CORS issues (same origin) | CORS issues (different domains) |

**Key Difference:**
- **Local:** Frontend and Backend both run locally → No CORS
- **Vercel:** Frontend and Backend on different domains → Need proper CORS headers

**Solution:**
- Set `REACT_APP_API_URL` in Vercel dashboard
- Ensure backend sends CORS headers (already configured in Flask)
- Remove `withCredentials: true` from axios (fixed in your code)

---

## 🔍 Debugging Checklist

### If Login Still Fails:

1. **Open DevTools Console** (F12)
   - Check for `🔐 Login Attempt` and `API URL` log
   - This tells you which API URL is being used

2. **Check Network Tab**
   - Look for POST request to `/api/student/login`
   - Check response status (200, 401, 404, 500, etc.)
   - Check response headers for `Access-Control-Allow-Origin`

3. **Verify Environment Variables**
   - Go to Vercel Dashboard → Settings → Environment Variables
   - Confirm `REACT_APP_API_URL` is set to backend URL
   - Trigger a rebuild after changing

4. **Test Backend Directly**
   - Run in browser: `https://classroom-assistant-backend.vercel.app/api/student/login`
   - Should return a 405 or 400 error (POST required)
   - If 404, backend is not deployed

5. **Check CSS Issues**
   - CSS is imported correctly in CRA
   - If missing on Vercel:
     - Clear browser cache (Ctrl+Shift+Delete)
     - Hard refresh (Ctrl+Shift+R)
     - Check build output in Vercel dashboard

---

## ✅ Testing Locally Before Vercel

```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd frontend
npm start

# Open http://localhost:3001
# Login should work
# Check console logs for API URL confirmation
```

---

## 📝 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Backend not reachable" | Check REACT_APP_API_URL in Vercel env vars |
| 404 on login | Backend URL is wrong or backend not deployed |
| 401 on login | Credentials are wrong (not an API issue) |
| CORS error | Remove `withCredentials: true` from axios |
| CSS missing | Clear cache, hard refresh (Ctrl+Shift+R) |
| Timeout errors | Backend is slow - check performance |

---

## 🔗 Your URLs

- **Frontend:** https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app
- **Backend:** https://classroom-assistant-backend.vercel.app
- **GitHub:** https://github.com/lakshmitarun/real-time-classroom-assistant

---

## ✨ Summary

**What was fixed:**
- ✅ Simplified `src/config/api.js` with better logging
- ✅ Enhanced error handling in `StudentView.js` with timeout
- ✅ Cleaned up `.env` and `.env.production` files
- ✅ Removed `withCredentials: true` (already done)
- ✅ Added timeout to axios requests (10 seconds)

**What to verify on Vercel:**
1. Environment variable `REACT_APP_API_URL` is set
2. Backend is deployed and running
3. CORS headers are enabled on backend (already configured)

**Next steps:**
1. Commit and push changes
2. Vercel auto-deploys
3. Test login in production
4. Check DevTools Console for logs

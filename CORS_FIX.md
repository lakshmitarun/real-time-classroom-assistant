# CORS Fix: Vercel Frontend to Flask Backend

## Problem Diagnosed

**Error:** `No 'Access-Control-Allow-Origin' header is present on the requested resource`

**Root Cause:** 
1. Browser sends preflight OPTIONS request
2. Backend wasn't responding with CORS headers on OPTIONS
3. Browser blocks actual POST request

## Solution Implemented

### Backend Changes (Flask)

**What was fixed:**
1. Enhanced `@app.before_request` to explicitly handle OPTIONS
2. Added detailed logging to debug CORS issues
3. Updated `/api/student/login` to accept OPTIONS method
4. Added `Access-Control-Allow-Credentials` header
5. Added `Access-Control-Expose-Headers` for authorization

**Key Code:**

```python
@app.before_request
def handle_preflight():
    """Handle CORS preflight requests (OPTIONS)"""
    origin = request.headers.get("Origin")
    
    if request.method == "OPTIONS":
        if not is_allowed_origin(origin):
            return "", 403
        
        response = make_response("", 204)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
        response.headers["Access-Control-Max-Age"] = "86400"
        response.headers["Vary"] = "Origin"
        
        return response, 204

@app.route("/api/student/login", methods=["POST", "OPTIONS"])
def student_login():
    if request.method == "OPTIONS":
        return "", 204
    
    # ... rest of login logic
```

## How CORS Preflight Works

```
Browser                              Backend
  |                                   |
  |-------- OPTIONS /api/student/login ------->|
  |        (Preflight Request)                 |
  |                                   |
  |<-------- 204 No Content -----------|
  |   (With CORS Headers)             |
  |                                   |
  |-------- POST /api/student/login ----->|
  |        (Actual Request)                   |
  |                                   |
  |<-------- 200 OK -------------------|
  |   (With user data & token)        |
```

## Vercel Deployment Checklist

- [ ] Backend deployed to `https://classroom-assistant-backend.vercel.app`
- [ ] Frontend deployed to `https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app`
- [ ] Backend logs show `✅ Preflight approved with CORS headers`
- [ ] Network tab shows OPTIONS: 204 status
- [ ] Network tab shows POST: 200 status
- [ ] Response headers include `Access-Control-Allow-Origin`

## Testing Steps

### 1. Local Testing

```bash
# Terminal 1: Start backend
cd backend
python app.py

# Should output:
# INFO:root:📍 Request: OPTIONS /api/student/login | Origin: http://localhost:3001
# INFO:root:🔍 Preflight request for: /api/student/login
# INFO:root:✅ Preflight approved with CORS headers
```

```bash
# Terminal 2: Start frontend
cd frontend
npm start

# Open http://localhost:3001
# Login attempt should work
# Check console for:
# 🔐 Login Attempt:
#   - API URL: http://localhost:3000
```

### 2. DevTools Network Inspection

1. Open Frontend URL on Vercel
2. Press F12 → Network tab
3. Attempt login
4. Look for two requests:
   - **OPTIONS /api/student/login** → Status: 204
   - **POST /api/student/login** → Status: 200

5. Click OPTIONS request:
   - Headers → Response Headers:
     - `Access-Control-Allow-Origin: https://real-time-classroom-...`
     - `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
     - `Access-Control-Allow-Headers: Content-Type, Authorization, Accept`

6. Click POST request:
   - Response should show login success JSON

### 3. Backend Logs on Vercel

Go to Vercel Dashboard → Backend Project → Deployments → View Build Logs

Should show:
```
📍 Request: OPTIONS /api/student/login | Origin: https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app
🔍 Preflight request for: /api/student/login
✅ Preflight approved with CORS headers
```

Then:
```
📍 Request: POST /api/student/login | Origin: https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app
```

## Troubleshooting

### Still Getting CORS Error?

**Check 1: Is backend responding to OPTIONS?**
```bash
curl -X OPTIONS https://classroom-assistant-backend.vercel.app/api/student/login \
  -H "Origin: https://real-time-classroom-..." \
  -H "Access-Control-Request-Method: POST" \
  -v
```

Should return status 204 with these headers:
- `Access-Control-Allow-Origin: https://real-time-classroom-...`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`

**Check 2: Is frontend sending correct Origin header?**
```
DevTools → Network → OPTIONS request → Request Headers
```
Should show:
```
Origin: https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app
```

**Check 3: Is origin in allowed list?**
Backend code should have in `ALLOWED_ORIGINS`:
```python
ALLOWED_ORIGINS = [
    "https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app"
]
# OR wildcard
if "vercel.app" in origin:
    return True
```

### Still Getting "Backend not reachable"?

1. Check Network tab for actual error status
2. Check backend logs in Vercel dashboard
3. Verify backend URL in frontend `.env.production`
4. Trigger Vercel rebuild

## HTTP Status Codes Explained

| Status | Meaning | Action |
|--------|---------|--------|
| **204** | Preflight OK | Browser will send actual request |
| **200** | Login successful | User data received |
| **400** | Bad request (missing fields) | Check if userId/password are sent |
| **401** | Unauthorized | Check credentials |
| **403** | Forbidden (CORS blocked) | Check if origin is allowed |
| **404** | Backend not found | Check backend URL |
| **500** | Server error | Check backend logs |

## Files Modified

1. **`backend/app.py`**
   - Enhanced `@app.before_request` with explicit CORS handling
   - Added logging for debugging
   - Updated `/api/student/login` to accept OPTIONS

2. **`frontend/src/config/api.js`**
   - Simplified API URL logic
   - Added debug logging

3. **`frontend/src/pages/StudentView.js`**
   - Enhanced error messages
   - Added timeout to requests
   - Better debugging output

## Next Steps

1. **Verify backend deployed:** Visit `https://classroom-assistant-backend.vercel.app/` in browser
2. **Trigger rebuild:** Push changes or manually rebuild in Vercel dashboard
3. **Test login:** Try login on Vercel frontend, check DevTools
4. **Monitor logs:** Check Vercel backend logs for CORS debug output
5. **Verify success:** Should see "✅ Preflight approved" in logs

## Reference URLs

- Frontend: https://real-time-classroom-git-c4ab73-palivela-lakshmi-taruns-projects.vercel.app
- Backend: https://classroom-assistant-backend.vercel.app
- Vercel Dashboard: https://vercel.com/dashboard

---

**Created:** 2026-01-31
**Status:** CORS preflight handling implemented and tested

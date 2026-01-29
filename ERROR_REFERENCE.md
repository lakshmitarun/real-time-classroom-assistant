# Error Reference Card

## Quick Error Reference

### Error Type 1: 404 Not Found
```
Error Message:
Failed to load resource: the server responded with a status of 404

What it means:
The backend endpoint doesn't exist or wrong URL is being called

What was wrong:
Frontend was calling http://localhost:5000 (doesn't exist in production)

How it's fixed:
Now calls https://classroom-assistant-backend.vercel.app (correct URL)

How to verify:
DevTools → Network tab → login request → URL should be vercel.app
```

---

### Error Type 2: CORS Blocked
```
Error Message:
Access to XMLHttpRequest at 'https://classroom-assistant-backend.vercel.app/api/student/login' 
from origin 'https://real-time-classroom-assistant-ye11.vercel.app' 
has been blocked by CORS policy: Response to preflight request doesn't 
pass access control check: No 'Access-Control-Allow-Origin' header 
is present on the requested resource.

What it means:
Browser blocked the request because:
1. Wrong domain is calling the backend, OR
2. Backend isn't sending proper CORS headers

What was wrong:
Frontend was trying to reach localhost from a different domain
(browsers block this for security)

How it's fixed:
1. Frontend now calls the correct backend (same domain)
2. Backend already has CORS headers configured

How to verify:
DevTools → Network tab → login request → Response headers 
should contain 'access-control-allow-origin'
```

---

### Error Type 3: Login error: br
```
Error Message:
Login error: br

What it means:
Generic error message that doesn't tell you what's wrong
(Could be CORS, 404, network, or API error)

What was wrong:
Error handling wasn't specific enough
No logging to help debug

How it's fixed:
1. Added console.log to show API URL being used
2. Added specific error messages:
   - "CORS error: ..." → CORS issue
   - "Backend server not found" → 404 issue
   - "Could not reach the backend server" → Network issue
   - "Invalid user ID or password" → Login failed

How to verify:
DevTools → Console tab → Look for "Login attempt with API URL: ..."
and specific error messages
```

---

## Common Scenarios

### Scenario A: Local Development
```
Frontend: http://localhost:3001
Backend:  http://localhost:5000

Frontend detects: NODE_ENV = 'development'
So uses: http://localhost:5000 ✓

Works perfectly for local testing
```

### Scenario B: Production on Vercel
```
Frontend: https://real-time-classroom-assistant-ye11.vercel.app
Backend:  https://classroom-assistant-backend.vercel.app

Frontend detects: NODE_ENV = 'production'
So uses: https://classroom-assistant-backend.vercel.app ✓

CORS headers from backend allow the request ✓
```

### Scenario C: Override (if needed)
```
Environment variable set: REACT_APP_API_URL=https://custom-backend.com

Frontend ignores NODE_ENV and uses: https://custom-backend.com ✓

Useful for:
- Testing with different backend
- Custom deployments
- Staging environments
```

---

## Browser DevTools Guide

### Network Tab
```
Step 1: Open DevTools (F12)
Step 2: Go to "Network" tab
Step 3: Try logging in
Step 4: Look for request ending in "login"
Step 5: Click on it
Step 6: Check "Response Headers"

Look for:
✓ access-control-allow-origin header
✓ access-control-allow-methods header
✓ Status code: 200 or 400 (not 404)
```

### Console Tab
```
Step 1: Open DevTools (F12)
Step 2: Go to "Console" tab
Step 3: Try logging in
Step 4: Look for messages:

✓ "Login attempt with API URL: https://..."
✓ Specific error message (if login fails)

Do NOT see:
✗ "Login error: br" (old error)
✗ CORS error messages
✗ 404 errors in red
```

---

## Fix Validation

### Checklist After Changes
- [ ] File `frontend/src/config/api.js` modified ✓
- [ ] File `frontend/src/pages/StudentView.js` modified ✓
- [ ] Changes committed and pushed ✓
- [ ] Vercel deployment completed ✓
- [ ] Browser cache cleared (Ctrl+Shift+Delete) ✓
- [ ] Can see "Login attempt with API URL:" in console ✓
- [ ] API URL points to vercel.app (not localhost) ✓
- [ ] No CORS errors in console ✓
- [ ] No 404 errors in network tab ✓

### After all checks pass:
```
✅ Frontend automatically uses correct backend
✅ CORS checks pass
✅ Errors are specific and helpful
✅ Ready for production use
```

---

## What NOT to Do

### ❌ Don't hardcode URLs
```javascript
// WRONG - breaks in different environments
const url = 'http://localhost:5000';

// RIGHT - works everywhere
const url = process.env.NODE_ENV === 'production' 
  ? 'https://backend.vercel.app' 
  : 'http://localhost:5000';
```

### ❌ Don't ignore error types
```javascript
// WRONG - unclear error
catch(error) { setError('Error'); }

// RIGHT - specific error
catch(error) {
  if (error.response?.status === 404) setError('Not found');
  if (error.message.includes('CORS')) setError('CORS error');
  // etc...
}
```

### ❌ Don't trust browser cache
```
// If code changes don't seem to take effect:
// Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
// Clear cache: Ctrl+Shift+Delete
```

---

## Quick Reference URLs

| Environment | Frontend URL | Backend URL |
|-------------|------|--------|
| Production | `https://real-time-classroom-assistant-ye11.vercel.app` | `https://classroom-assistant-backend.vercel.app` |
| Development | `http://localhost:3001` | `http://localhost:5000` |

---

## Helpful Commands

```bash
# Test backend directly
curl https://classroom-assistant-backend.vercel.app/api/student/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","password":"test"}'

# View Vercel logs
vercel logs

# Check git changes
git status
git diff

# Revert changes if needed
git revert HEAD
git push
```

---

## Support Resources

| Issue | Resource |
|-------|----------|
| CORS errors | See "Error Type 2" above |
| 404 errors | See "Error Type 1" above |
| Unclear errors | See "Error Type 3" above |
| DevTools usage | See "Browser DevTools Guide" above |
| Local setup | See "Scenario A" above |
| Production setup | See "Scenario B" above |

---

**Remember: The error "Login error: br" is now replaced with specific, helpful messages!** 🎯

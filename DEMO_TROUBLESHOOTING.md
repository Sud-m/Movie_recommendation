# Demo Troubleshooting Guide

## Quick Test Steps

### 1. Check if Backend is Running
```bash
cd backend
source venv/bin/activate
python app.py
```

Should see: `* Running on http://127.0.0.1:5000`

### 2. Test Demo API Directly
Open in browser or use curl:
```bash
curl http://localhost:5000/api/demo/users
```

Should return JSON with three users: sarah, james, emma

### 3. Check Frontend
```bash
cd frontend
npm start
```

Navigate to: `http://localhost:3000/demo`

### 4. Check Browser Console
Open Developer Tools (F12) and check Console tab for:
- "Demo page loaded"
- "API_URL: http://localhost:5000"
- "Fetching demo users from: ..."
- "Demo users response: ..."

## Common Issues

### Issue: Blank Page
**Symptoms**: Page loads but shows nothing

**Solutions**:
1. Check browser console for errors
2. Look for the yellow warning box that says "No users loaded"
3. Verify backend is running
4. Test API endpoint directly

### Issue: "Back to App" redirects to login
**Fixed**: Button now says "Back to Login" and goes to `/login`

### Issue: API not found (404)
**Check**:
1. Is `demo_bp` imported in `backend/app.py`?
2. Is `demo_bp` registered with `app.register_blueprint(demo_bp)`?
3. Restart backend server after changes

### Issue: CORS error
**Should be handled** by the existing CORS config in app.py

### Issue: Network error
**Check**:
1. Backend running on port 5000?
2. Frontend able to reach backend?
3. Try `curl http://localhost:5000/api/demo/users`

## Expected Behavior

1. Navigate to `/demo`
2. See introduction banner with GRAFTER-Rec info
3. See three persona cards: Sarah, James, Emma
4. Click a persona to see their profile and recommendations
5. Rate movies to see recommendations update
6. Click "Show Full Explanation" to see graph paths

## Debug Mode

The demo page now has built-in debugging:
- Console logs show API calls and responses
- Yellow warning box appears if no users loaded
- Error screen shows if API fails
- Loading spinner shows while fetching

## Manual Test

Test the API manually:

```bash
# Test users endpoint
curl http://localhost:5000/api/demo/users

# Test user profile
curl http://localhost:5000/api/demo/user/sarah

# Test recommendations
curl http://localhost:5000/api/demo/recommendations/sarah
```

All should return valid JSON.


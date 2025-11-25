# Quick Setup Guide

Follow these steps to get your CSE573 Movie Recommendation Platform running locally.

## Step 1: Install PostgreSQL

### macOS
```bash
brew install postgresql@14
brew services start postgresql@14
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Windows
Download and install from: https://www.postgresql.org/download/windows/

## Step 2: Create Database

```bash
# Create the database
createdb netflix_clone

# Verify it was created
psql -l | grep netflix_clone
```

## Step 3: Get TMDB API Key

1. Go to https://www.themoviedb.org/signup
2. Create a free account
3. Go to Settings → API
4. Request an API key (Developer option)
5. Copy your **API Read Access Token** (starts with "eyJ...")

## Step 4: Backend Setup

```bash
# Navigate to backend directory
cd App/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://localhost/netflix_clone
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
TMDB_API_KEY=YOUR_TMDB_API_KEY_HERE
EOF

# IMPORTANT: Edit .env and replace YOUR_TMDB_API_KEY_HERE with your actual key!
nano .env  # or use your preferred editor

# Initialize database (optional, app.py does this automatically)
python init_db.py

# Run the backend
python app.py
```

Backend should now be running on http://localhost:5000

## Step 5: Frontend Setup

Open a NEW terminal window:

```bash
# Navigate to frontend directory
cd App/frontend

# Install dependencies
npm install

# Start the development server
npm start
```

Frontend should now be running on http://localhost:3000

## Step 6: Test the Application

1. Open http://localhost:3000 in your browser
2. Click "Sign up now" to create an account
3. Enter your email, username, and password
4. You should be redirected to the home page with movies!

## Verification Checklist

✓ PostgreSQL is installed and running
✓ Database 'netflix_clone' exists
✓ Backend virtual environment activated
✓ Dependencies installed (pip install)
✓ .env file created with TMDB API key
✓ Backend running on port 5000
✓ Frontend dependencies installed (npm install)
✓ Frontend running on port 3000
✓ Can register/login successfully
✓ Movies are loading on the home page

## Common Issues

### "Database connection failed"
- Make sure PostgreSQL is running: `pg_isready`
- Verify database exists: `psql -l | grep netflix_clone`
- Check DATABASE_URL in .env file

### "Movies not loading" or "TMDB API error"
- Verify TMDB_API_KEY in .env file
- Make sure you're using the **API Read Access Token**, not the API Key
- Check backend console for error messages

### "Port already in use"
- Kill process on port 5000: `lsof -ti:5000 | xargs kill -9`
- Or change port in app.py: `app.run(debug=True, port=5001)`

### "Module not found" errors
- Backend: Make sure virtual environment is activated
- Frontend: Run `npm install` again

## Need Help?

Check the full README.md for detailed documentation and troubleshooting.


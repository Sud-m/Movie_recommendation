# Quick Start Guide

## ✅ What's Already Done

- ✅ Backend virtual environment created (`backend/venv/`)
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed
- ✅ `.env` file created with secret keys

## 🔧 What You Need to Do

### Step 1: Install PostgreSQL

PostgreSQL is required for the database. Install it using Homebrew:

```bash
brew install postgresql@14
brew services start postgresql@14
```

**Note:** After installation, you may need to add PostgreSQL to your PATH. Add this to your `~/.zshrc`:
```bash
export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"
```
Then run: `source ~/.zshrc`

### Step 2: Create the Database

```bash
createdb netflix_clone
```

Verify it was created:
```bash
psql -l | grep netflix_clone
```

### Step 3: Get TMDB API Key

1. Go to https://www.themoviedb.org/signup
2. Create a free account
3. Go to Settings → API
4. Request an API key (Developer option)
5. Copy your **API Read Access Token** (starts with "eyJ...")

### Step 4: Add TMDB API Key to .env

Edit `backend/.env` and replace `YOUR_TMDB_API_KEY_HERE` with your actual TMDB API key:

```bash
nano backend/.env
# or use your preferred editor
```

### Step 5: Initialize Database

```bash
cd backend
source venv/bin/activate
python init_db.py
```

### Step 6: Start the Backend Server

In Terminal 1:
```bash
cd backend
source venv/bin/activate
python app.py
```

The backend should start on `http://localhost:5000`

### Step 7: Start the Frontend Server

In Terminal 2 (new terminal window):
```bash
cd frontend
npm start
```

The frontend should start on `http://localhost:3000`

## 🎉 You're Done!

Open your browser and go to `http://localhost:3000` to use the app!

## 🐛 Troubleshooting

### PostgreSQL Issues
- If `createdb` command not found, make sure PostgreSQL is in your PATH
- Check if PostgreSQL is running: `pg_isready`
- Verify database exists: `psql -l | grep netflix_clone`

### Backend Issues
- Make sure virtual environment is activated: `source venv/bin/activate`
- Check `.env` file has correct TMDB_API_KEY
- Verify database connection in `.env` matches your PostgreSQL setup

### Frontend Issues
- Make sure backend is running first (port 5000)
- Clear npm cache if needed: `npm cache clean --force`
- Reinstall dependencies: `rm -rf node_modules && npm install`

### Port Conflicts
- If port 5000 is in use: Edit `backend/app.py` and change port
- If port 3000 is in use: `PORT=3001 npm start`


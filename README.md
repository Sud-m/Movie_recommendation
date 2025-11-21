# CSE573 Movie Recommendation Platform

A full-stack movie recommendation platform built with React (using Tailwind CSS) and Flask, featuring authentication, TMDB API integration, watchlist functionality, and movie recommendations.

## Features

- 🔐 **User Authentication**: JWT-based authentication with login/register
- 🎬 **Movie Browsing**: Browse trending, popular, top-rated, now playing, and upcoming movies
- 🔍 **Search**: Search for movies by title
- ❤️ **Watchlist**: Add/remove movies to your personal watchlist
- 🎨 **Modern UI**: Beautiful, responsive UI built with Tailwind CSS
- 🎥 **Movie Details**: View detailed information about movies including cast, directors, genres, and trailers

## Tech Stack

### Backend
- Flask (Python web framework)
- PostgreSQL (Database)
- Flask-SQLAlchemy (ORM)
- Flask-JWT-Extended (Authentication)
- TMDB API (Movie data)

### Frontend
- React 18
- React Router v6
- Axios (HTTP client)
- Tailwind CSS (Styling)

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- TMDB API Key (get from https://www.themoviedb.org/settings/api)

## Setup Instructions

### 1. Database Setup

First, create a PostgreSQL database:

```bash
# Start PostgreSQL (if not already running)
brew services start postgresql  # macOS
# or
sudo systemctl start postgresql  # Linux

# Create database
createdb netflix_clone

# Or using psql:
psql postgres
CREATE DATABASE netflix_clone;
\q
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd App/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env and add your configuration:
# - DATABASE_URL=postgresql://localhost/netflix_clone
# - TMDB_API_KEY=your_tmdb_api_key_here
# - SECRET_KEY=your-secret-key
# - JWT_SECRET_KEY=your-jwt-secret-key

# Run the Flask app
python app.py
```

The backend will start on `http://localhost:5000`

### 3. Frontend Setup

```bash
# Open a new terminal
# Navigate to frontend directory
cd App/frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will start on `http://localhost:3000`

## Environment Variables

### Backend (.env)

Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=postgresql://localhost/netflix_clone
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
TMDB_API_KEY=your-tmdb-api-key-here
```

### Get TMDB API Key

1. Go to https://www.themoviedb.org/
2. Create an account
3. Go to Settings > API
4. Request an API key (choose "Developer" option)
5. Copy the API key and add it to your `.env` file

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires auth)

### Movies
- `GET /api/movies/trending` - Get trending movies
- `GET /api/movies/popular` - Get popular movies
- `GET /api/movies/top-rated` - Get top rated movies
- `GET /api/movies/now-playing` - Get now playing movies
- `GET /api/movies/upcoming` - Get upcoming movies
- `GET /api/movies/genres` - Get movie genres
- `GET /api/movies/by-genre/:genreId` - Get movies by genre
- `GET /api/movies/:movieId` - Get movie details
- `GET /api/movies/search?q=query` - Search movies

### Watchlist (requires authentication)
- `GET /api/movies/watchlist` - Get user's watchlist
- `POST /api/movies/watchlist` - Add movie to watchlist
- `DELETE /api/movies/watchlist/:movieId` - Remove movie from watchlist
- `GET /api/movies/watchlist/check/:movieId` - Check if movie is in watchlist

## Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique email address
- `username` - Unique username
- `password_hash` - Hashed password
- `created_at` - Account creation timestamp

### Watchlist Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `movie_id` - TMDB movie ID
- `movie_title` - Movie title
- `movie_poster` - Poster path
- `movie_backdrop` - Backdrop path
- `added_at` - Timestamp when added

## Usage

1. **Register/Login**: Create an account or login on the landing page
2. **Browse Movies**: Scroll through different categories of movies
3. **Search**: Use the search bar to find specific movies
4. **View Details**: Click on any movie to see detailed information
5. **Add to Watchlist**: Click "+ Add to List" to save movies
6. **My List**: Access your watchlist from the navigation menu

## Troubleshooting

### Database Connection Issues

If you get database connection errors:

```bash
# Check if PostgreSQL is running
pg_isready

# Verify database exists
psql -l | grep netflix_clone

# Test connection
psql netflix_clone
```

### TMDB API Issues

If movies aren't loading:

1. Verify your TMDB API key is correct in `.env`
2. Check the Flask console for error messages
3. Ensure you're using the API Read Access Token (Bearer token), not the API Key

### Port Conflicts

If ports 3000 or 5000 are already in use:

**Frontend:**
```bash
PORT=3001 npm start
```

**Backend:**
Edit `app.py` and change the port:
```python
app.run(debug=True, port=5001)
```

## Development Notes

- The database tables are automatically created when you first run `app.py`
- All passwords are hashed using werkzeug's security functions
- JWT tokens expire after 1 hour (configurable in `config.py`)
- CORS is enabled for local development

## Future Enhancements

- [ ] Video streaming/trailer integration
- [ ] User profiles with avatars
- [ ] Movie recommendations based on watchlist
- [ ] Social features (sharing, comments)
- [ ] Multiple user profiles per account
- [ ] Email verification
- [ ] Password reset functionality
- [ ] Dark/light theme toggle

## License

This is a demonstration project for educational purposes.

## Credits

- Movie data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/)
- Built for CSE573 Course Project


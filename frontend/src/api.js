import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response (likely CORS or network issue)
      console.error('Network Error:', error.message);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (email, username, password) =>
    api.post('/auth/register', { email, username, password }),
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  getCurrentUser: () =>
    api.get('/auth/me'),
};

// Movies API
export const moviesAPI = {
  getTrending: (page = 1) =>
    api.get('/movies/trending', { params: { page } }),
  getPopular: (page = 1) =>
    api.get('/movies/popular', { params: { page } }),
  getTopRated: (page = 1) =>
    api.get('/movies/top-rated', { params: { page } }),
  getNowPlaying: (page = 1) =>
    api.get('/movies/now-playing', { params: { page } }),
  getUpcoming: (page = 1) =>
    api.get('/movies/upcoming', { params: { page } }),
  getByGenre: (genreId, page = 1) =>
    api.get(`/movies/by-genre/${genreId}`, { params: { page } }),
  getMovieDetails: (movieId) =>
    api.get(`/movies/${movieId}`),
  searchMovies: (query, page = 1) =>
    api.get('/movies/search', { params: { q: query, page } }),
  getGenres: () =>
    api.get('/movies/genres'),
  
  // Watchlist
  getWatchlist: () =>
    api.get('/movies/watchlist'),
  addToWatchlist: (movie) =>
    api.post('/movies/watchlist', {
      movie_id: movie.id,
      title: movie.title,
      poster_path: movie.poster_path,
      backdrop_path: movie.backdrop_path,
    }),
  removeFromWatchlist: (movieId) =>
    api.delete(`/movies/watchlist/${movieId}`),
  checkInWatchlist: (movieId) =>
    api.get(`/movies/watchlist/check/${movieId}`),
  getRecommendations: ({ mode = 'graph', limit = 10, demoUserId, movieId } = {}) =>
    api.get('/recommendations', {
      params: {
        mode,
        limit,
        demo_user_id: demoUserId,
        movie_id: movieId,
      },
    }),
};

// TMDB image helper
export const getImageUrl = (path, size = 'w500') => {
  if (!path) return 'https://via.placeholder.com/500x750?text=No+Image';
  return `https://image.tmdb.org/t/p/${size}${path}`;
};

export default api;


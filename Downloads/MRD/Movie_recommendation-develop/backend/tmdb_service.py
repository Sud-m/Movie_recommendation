import requests
from flask import current_app


class TMDBService:
    """Service for interacting with TMDB API"""
    
    @staticmethod
    def _get_headers():
        """Get headers for TMDB API requests"""
        api_key = current_app.config['TMDB_API_KEY']
        return {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json;charset=utf-8'
        }
    
    @staticmethod
    def _make_request(endpoint, params=None):
        """Make request to TMDB API"""
        base_url = current_app.config['TMDB_BASE_URL']
        url = f"{base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=TMDBService._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"TMDB API Error: {e}")
            return None
    
    @staticmethod
    def get_trending_movies(time_window='week', page=1):
        """Get trending movies"""
        return TMDBService._make_request(f'/trending/movie/{time_window}', {'page': page})
    
    @staticmethod
    def get_popular_movies(page=1):
        """Get popular movies"""
        return TMDBService._make_request('/movie/popular', {'page': page})
    
    @staticmethod
    def get_top_rated_movies(page=1):
        """Get top rated movies"""
        return TMDBService._make_request('/movie/top_rated', {'page': page})
    
    @staticmethod
    def get_now_playing_movies(page=1):
        """Get now playing movies"""
        return TMDBService._make_request('/movie/now_playing', {'page': page})
    
    @staticmethod
    def get_upcoming_movies(page=1):
        """Get upcoming movies"""
        return TMDBService._make_request('/movie/upcoming', {'page': page})
    
    @staticmethod
    def get_movie_by_genre(genre_id, page=1):
        """Get movies by genre"""
        params = {
            'with_genres': genre_id,
            'page': page,
            'sort_by': 'popularity.desc'
        }
        return TMDBService._make_request('/discover/movie', params)
    
    @staticmethod
    def get_movie_details(movie_id):
        """Get detailed information about a movie"""
        return TMDBService._make_request(f'/movie/{movie_id}', {
            'append_to_response': 'videos,credits,similar'
        })
    
    @staticmethod
    def search_movies(query, page=1):
        """Search for movies"""
        return TMDBService._make_request('/search/movie', {
            'query': query,
            'page': page
        })
    
    @staticmethod
    def get_genres():
        """Get list of movie genres"""
        return TMDBService._make_request('/genre/movie/list')


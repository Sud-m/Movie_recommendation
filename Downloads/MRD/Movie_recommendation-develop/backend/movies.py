from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from tmdb_service import TMDBService
from models import db, Watchlist, Rating
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

movies_bp = Blueprint('movies', __name__, url_prefix='/api/movies')


@movies_bp.route('/trending', methods=['GET'])
def get_trending():
    """Get trending movies"""
    page = request.args.get('page', 1, type=int)
    time_window = request.args.get('time_window', 'week')
    
    result = TMDBService.get_trending_movies(time_window, page)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Failed to fetch trending movies'}), 500


@movies_bp.route('/popular', methods=['GET'])
def get_popular():
    """Get popular movies"""
    page = request.args.get('page', 1, type=int)
    
    result = TMDBService.get_popular_movies(page)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Failed to fetch popular movies'}), 500


@movies_bp.route('/top-rated', methods=['GET'])
def get_top_rated():
    """Get top rated movies"""
    page = request.args.get('page', 1, type=int)
    
    result = TMDBService.get_top_rated_movies(page)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Failed to fetch top rated movies'}), 500


@movies_bp.route('/now-playing', methods=['GET'])
def get_now_playing():
    """Get now playing movies"""
    page = request.args.get('page', 1, type=int)
    
    result = TMDBService.get_now_playing_movies(page)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Failed to fetch now playing movies'}), 500


@movies_bp.route('/upcoming', methods=['GET'])
def get_upcoming():
    """Get upcoming movies"""
    page = request.args.get('page', 1, type=int)
    
    result = TMDBService.get_upcoming_movies(page)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Failed to fetch upcoming movies'}), 500


@movies_bp.route('/genres', methods=['GET'])
def get_genres():
    """Get movie genres"""
    result = TMDBService.get_genres()
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Failed to fetch genres'}), 500


@movies_bp.route('/by-genre/<int:genre_id>', methods=['GET'])
def get_by_genre(genre_id):
    """Get movies by genre"""
    page = request.args.get('page', 1, type=int)
    
    result = TMDBService.get_movie_by_genre(genre_id, page)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Failed to fetch movies by genre'}), 500


@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """Get movie details"""
    result = TMDBService.get_movie_details(movie_id)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Failed to fetch movie details'}), 500


@movies_bp.route('/search', methods=['GET'])
def search_movies():
    """Search for movies"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    result = TMDBService.search_movies(query, page)
    if result:
        return jsonify(result), 200
    return jsonify({'error': 'Failed to search movies'}), 500


# Watchlist endpoints
@movies_bp.route('/watchlist', methods=['GET'])
@jwt_required()
def get_watchlist():
    """Get user's watchlist"""
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        watchlist = Watchlist.query.filter_by(user_id=user_id).order_by(Watchlist.added_at.desc()).all()
        
        return jsonify({
            'watchlist': [item.to_dict() for item in watchlist]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/watchlist', methods=['POST'])
@jwt_required()
def add_to_watchlist():
    """Add movie to watchlist"""
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        data = request.get_json()
        
        if not data or 'movie_id' not in data:
            return jsonify({'error': 'Movie ID is required'}), 400
        
        # Create watchlist entry
        watchlist_item = Watchlist(
            user_id=user_id,
            movie_id=data['movie_id'],
            movie_title=data.get('title', ''),
            movie_poster=data.get('poster_path', ''),
            movie_backdrop=data.get('backdrop_path', '')
        )
        
        db.session.add(watchlist_item)
        db.session.commit()
        
        return jsonify({
            'message': 'Movie added to watchlist',
            'item': watchlist_item.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Movie already in watchlist'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/watchlist/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def remove_from_watchlist(movie_id):
    """Remove movie from watchlist"""
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        
        watchlist_item = Watchlist.query.filter_by(
            user_id=user_id,
            movie_id=movie_id
        ).first()
        
        if not watchlist_item:
            return jsonify({'error': 'Movie not found in watchlist'}), 404
        
        db.session.delete(watchlist_item)
        db.session.commit()
        
        return jsonify({'message': 'Movie removed from watchlist'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/watchlist/check/<int:movie_id>', methods=['GET'])
@jwt_required()
def check_in_watchlist(movie_id):
    """Check if movie is in user's watchlist"""
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        
        exists = Watchlist.query.filter_by(
            user_id=user_id,
            movie_id=movie_id
        ).first() is not None
        
        return jsonify({'in_watchlist': exists}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rating endpoints
@movies_bp.route('/<int:movie_id>/rate', methods=['POST'])
@jwt_required()
def rate_movie(movie_id):
    """Create or update user's rating for a movie"""
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        data = request.get_json()
        
        if not data or 'rating' not in data:
            return jsonify({'error': 'Rating is required'}), 400
        
        rating_value = float(data['rating'])
        
        # Validate rating (0.5 to 5.0 in 0.5 increments)
        if rating_value < 0.5 or rating_value > 5.0:
            return jsonify({'error': 'Rating must be between 0.5 and 5.0'}), 400
        
        # Check if rating already exists
        existing_rating = Rating.query.filter_by(
            user_id=user_id,
            movie_id=movie_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_value
            db.session.commit()
            return jsonify({
                'message': 'Rating updated successfully',
                'rating': existing_rating.to_dict()
            }), 200
        else:
            # Create new rating
            new_rating = Rating(
                user_id=user_id,
                movie_id=movie_id,
                rating=rating_value
            )
            db.session.add(new_rating)
            db.session.commit()
            return jsonify({
                'message': 'Rating added successfully',
                'rating': new_rating.to_dict()
            }), 201
        
    except ValueError:
        return jsonify({'error': 'Invalid rating value'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/<int:movie_id>/rating', methods=['GET'])
@jwt_required()
def get_user_rating(movie_id):
    """Get user's rating for a movie"""
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        
        rating = Rating.query.filter_by(
            user_id=user_id,
            movie_id=movie_id
        ).first()
        
        if rating:
            return jsonify({'rating': rating.to_dict()}), 200
        else:
            return jsonify({'rating': None}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/<int:movie_id>/ratings', methods=['GET'])
def get_movie_ratings(movie_id):
    """Get average rating and count for a movie"""
    try:
        result = db.session.query(
            func.avg(Rating.rating).label('average_rating'),
            func.count(Rating.id).label('rating_count')
        ).filter_by(movie_id=movie_id).first()
        
        average_rating = float(result.average_rating) if result.average_rating else None
        rating_count = result.rating_count if result.rating_count else 0
        
        return jsonify({
            'average_rating': round(average_rating, 2) if average_rating else None,
            'rating_count': rating_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/<int:movie_id>/rate', methods=['DELETE'])
@jwt_required()
def delete_rating(movie_id):
    """Delete user's rating for a movie"""
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        
        rating = Rating.query.filter_by(
            user_id=user_id,
            movie_id=movie_id
        ).first()
        
        if not rating:
            return jsonify({'error': 'Rating not found'}), 404
        
        db.session.delete(rating)
        db.session.commit()
        
        return jsonify({'message': 'Rating deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


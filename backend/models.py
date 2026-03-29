from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    watchlist = db.relationship('Watchlist', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat()
        }


class Watchlist(db.Model):
    """User watchlist/favorites model"""
    __tablename__ = 'watchlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)  # TMDB movie ID
    movie_title = db.Column(db.String(255), nullable=False)
    movie_poster = db.Column(db.String(255))
    movie_backdrop = db.Column(db.String(255))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite unique constraint to prevent duplicate entries
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie'),)
    
    def to_dict(self):
        """Convert watchlist item to dictionary"""
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'movie_title': self.movie_title,
            'movie_poster': self.movie_poster,
            'movie_backdrop': self.movie_backdrop,
            'added_at': self.added_at.isoformat()
        }


from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
import re

from config import Config
from models import db
from auth import auth_bp
from movies import movies_bp
from recommendations import recommendations_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
# Allow multiple localhost ports for development
# Using regex pattern to allow any localhost/127.0.0.1 origin for easier development
CORS(app, 
     origins=re.compile(r'https?://(localhost|127\.0\.0\.1)(:\d+)?$'),
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type", "Authorization"],
     supports_credentials=True)
db.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(movies_bp)
app.register_blueprint(recommendations_bp)


@app.route('/')
def home():
    return jsonify({
        "message": "CSE573 Movie Recommendation Platform API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "movies": "/api/movies"
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "database": db_status
    })


# Create database tables (commented out after initial setup)
# Uncomment this on first run to create tables, or use init_db.py
# with app.app_context():
#     db.create_all()
#     print("Database tables created successfully!")


if __name__ == '__main__':
    app.run(debug=True, port=5000)

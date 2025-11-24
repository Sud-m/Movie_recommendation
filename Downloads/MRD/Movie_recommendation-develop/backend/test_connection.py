"""Quick test to verify database connection"""
from app import app
from models import db

with app.app_context():
    try:
        db.session.execute(db.text('SELECT 1'))
        print("SUCCESS: Backend can connect to database!")
    except Exception as e:
        print(f"ERROR: {e}")



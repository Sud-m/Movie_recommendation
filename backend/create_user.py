"""
Create a user in the database
Usage: python create_user.py
"""

from app import app, db
from models import User

def create_user(email, username, password):
    """Create a new user with hashed password"""
    with app.app_context():
        normalized_email = email.strip().lower()
        normalized_username = username.strip()
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == normalized_email) | (User.username == normalized_username)
        ).first()
        
        if existing_user:
            print(f"❌ User already exists!")
            print(f"   Email: {existing_user.email}")
            print(f"   Username: {existing_user.username}")
            return
        
        # Create new user
        user = User(email=normalized_email, username=normalized_username)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print("✓ User created successfully!")
        print(f"  Email: {email}")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"\nYou can now login with these credentials!")

if __name__ == '__main__':
    # Create the SWM user
    create_user(
        email='SWM@gmail.com',
        username='SWM',
        password='HelloWorld'
    )


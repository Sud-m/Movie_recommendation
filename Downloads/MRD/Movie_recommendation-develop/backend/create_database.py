"""
Script to create the netflix_clone database
Run this after setting up your .env file with the correct PostgreSQL password
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Get database URL from .env
db_url = os.getenv('DATABASE_URL', '')

if not db_url or 'YOUR_POSTGRES_PASSWORD' in db_url:
    print("ERROR: Please edit backend/.env file and replace YOUR_POSTGRES_PASSWORD with your actual PostgreSQL password")
    exit(1)

# Extract base URL (without database name) to connect to 'postgres' database
# Format: postgresql://user:password@host:port/database
if '/netflix_clone' in db_url:
    base_url = db_url.rsplit('/', 1)[0]  # Remove database name
else:
    base_url = db_url

# Connect to PostgreSQL server (using 'postgres' database to create new database)
try:
    print("Connecting to PostgreSQL server...")
    engine = create_engine(base_url + '/postgres')
    
    with engine.connect() as conn:
        # Check if database already exists
        result = conn.execute(text(
            "SELECT 1 FROM pg_database WHERE datname = 'netflix_clone'"
        ))
        exists = result.fetchone()
        
        if exists:
            print("SUCCESS: Database 'netflix_clone' already exists!")
        else:
            # Create database
            conn.execute(text("COMMIT"))  # End any transaction
            conn.execute(text("CREATE DATABASE netflix_clone"))
            conn.commit()
            print("SUCCESS: Database 'netflix_clone' created successfully!")
            
except Exception as e:
    print(f"ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure PostgreSQL is running")
    print("2. Check your password in .env file")
    print("3. Verify DATABASE_URL format: postgresql://postgres:password@localhost:5432/netflix_clone")
    exit(1)


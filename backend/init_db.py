"""
Database initialization script
Run this to create the database tables
"""

from app import app, db
from models import User, Watchlist

def init_database():
    """Initialize database tables"""
    with app.app_context():
        # Drop all tables (use with caution in production!)
        # db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("✓ Database tables created successfully!")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n✓ Created tables: {', '.join(tables)}")
        
        # Print table schemas
        for table_name in tables:
            print(f"\n{table_name.upper()} TABLE COLUMNS:")
            columns = inspector.get_columns(table_name)
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")

if __name__ == '__main__':
    init_database()


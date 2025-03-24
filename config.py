import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key')
    
    # Get database URL with proper validation
    DB_URL = os.environ.get('postgresql://dutgreivanceportal_user:bxnLojOc7vZDSnS6h1mDPDwcUK0v0IFZ@dpg-cvgr7h8fnakc73elosj0-a.oregon-postgres.render.com/dutgreivanceportal', '')
    if not DB_URL:
        raise ValueError("No DATABASE_URL set in environment variables")
        
    SQLALCHEMY_DATABASE_URI = DB_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

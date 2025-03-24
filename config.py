import os

class Config:
    # Get from environment variables (never hardcode!)
    SECRET_KEY = os.environ.get('SECRET_KEY')  
    
    # Let Render auto-inject DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://', 1
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

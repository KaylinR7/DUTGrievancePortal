import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    # Get Render's database URL and convert from postgres:// to postgresql://
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://dutgreivanceportal_user:bxnLojOc7vZDSnS6h1mDPDwcUK0v0IFZ@dpg-cvgr7h8fnakc73elosj0-a.oregon-postgres.render.com/dutgreivanceportal', '').replace(
        'postgres://', 'postgresql://', 1
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

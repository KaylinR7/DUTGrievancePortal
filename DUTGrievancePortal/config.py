import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://dutgreivanceportal_user:bxnLojOc7vZDSnS6h1mDPDwcUK0v0IFZ@dpg-cvgr7h8fnakc73elosj0-a.oregon-postgres.render.com/dutgreivanceportal')  # Get the database URL from Render
    SQLALCHEMY_TRACK_MODIFICATIONS = False

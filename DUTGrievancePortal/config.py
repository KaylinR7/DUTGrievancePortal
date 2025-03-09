import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Users/goven/Desktop/DUTGrievancePortal/DUTGrievancePortal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Removed all email-related configurations
import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Encode password if it contains special characters
    password = "sa13ir_S#"
    encoded_password = quote_plus(password)
    
    # Azure SQL Database connection string
    SQLALCHEMY_DATABASE_URI = (
        f'mssql+pyodbc://Samir:{encoded_password}@dutgrievanceportaldbserver.database.windows.net:1433/DUTGrievancePortal_db?driver=ODBC+Driver+17+for+SQL+Server'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 0  # Optional: Disable pooling for debugging

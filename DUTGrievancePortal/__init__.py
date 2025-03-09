from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config

# Initialize extensions outside the app factory
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    # Add these login manager configurations
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Ensure this matches your login route
    login_manager.login_message_category = 'danger'
    
    # ... rest of the code ...
    
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
from flask import Flask
from .config import Config
from .extensions import db, login_manager
from .routes import main_bp, staff_bp, admin_bp
from flask_migrate import Migrate

def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'danger'

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)  # Add this line to initialize migrations

    # Register blueprints with proper prefixes
    app.register_blueprint(main_bp)
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app

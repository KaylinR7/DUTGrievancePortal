from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from .routes import main_bp  # Update with your actual blueprint
    app.register_blueprint(main_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0')

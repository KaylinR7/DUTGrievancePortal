import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the app and database
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Set up database URI from environment variable
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('postgresql://dutgreivanceportal_user:bxnLojOc7vZDSnS6h1mDPDwcUK0v0IFZ@dpg-cvgr7h8fnakc73elosj0-a.oregon-postgres.render.com/dutgreivanceportal')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

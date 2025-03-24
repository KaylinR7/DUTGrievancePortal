import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the app and database
db = SQLAlchemy()

app = Flask(__name__)

# Set up database URI directly (you don't need os.getenv() here if the URI is a static string)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dutgreivanceportal_user:bxnLojOc7vZDSnS6h1mDPDwcUK0v0IFZ@dpg-cvgr7h8fnakc73elosj0-a.oregon-postgres.render.com/dutgreivanceportal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

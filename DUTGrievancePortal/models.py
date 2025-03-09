from DUTGrievancePortal import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    student_staff_number = db.Column(db.String(8), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    complaints = db.relationship('Complaint', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    sub_topic = db.Column(db.String(50))
    subject_line = db.Column(db.String(100))
    description = db.Column(db.Text)
    reference_id = db.Column(db.String(20), unique=True)
    status = db.Column(db.String(20), default='Pending')
    attachment_path = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)  # ? Correct syntax
    is_read = db.Column(db.Boolean, default=False)       # ? Correct syntax
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
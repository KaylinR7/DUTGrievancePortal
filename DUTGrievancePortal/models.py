from DUTGrievancePortal import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_staff_number = db.Column(db.String(8), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # New field
    first_name = db.Column(db.String(50), nullable=False)  # New field
    last_name = db.Column(db.String(50), nullable=False)  # New field
    password_hash = db.Column(db.String(128), nullable=False)
    is_staff = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Add these methods
    @property
    def password(self):
        raise AttributeError('Password is not readable')
    
    @password.setter
    def password(self, password):
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
    message = db.Column(db.Text) 
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaint = db.relationship('Complaint', backref=db.backref('feedback', lazy=True, cascade="all, delete"))
    user = db.relationship('User', backref=db.backref('feedback', lazy=True, cascade="all, delete"))

class ComplaintUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    updated_by = db.Column(db.String(255), nullable=False)
    update_text = db.Column(db.Text, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)

    complaint = db.relationship('Complaint', backref=db.backref('updates', lazy=True, cascade="all, delete"))

class Escalation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    escalated_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.Text, nullable=False)
    resolved = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('escalations', lazy=True, cascade="all, delete"))

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_num = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    initial = db.Column(db.String(10), nullable=False)
    surname = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    parent_category = db.relationship('Category', remote_side=[id], backref=db.backref('subcategories', lazy=True))

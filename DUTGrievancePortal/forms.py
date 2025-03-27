from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from .models import User  # Add this import

from wtforms import StringField, PasswordField, BooleanField, validators

from wtforms import StringField, PasswordField, BooleanField, validators

class LoginForm(FlaskForm):
    student_staff_number = StringField('Student/Staff Number', validators=[
        validators.InputRequired(),
        validators.Length(min=6, message="Number must be at least 8 characters")
    ])
    password = PasswordField('Password', validators=[validators.InputRequired()])
    remember = BooleanField('Remember Me')
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    student_staff_number = StringField('Student/Staff Number', 
                                     validators=[DataRequired(), Length(min=4, max=8)])
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_student_staff_number(self, student_staff_number):
        user = User.query.filter_by(student_staff_number=student_staff_number.data).first()
        if user:
            raise ValidationError('This student/staff number is already registered.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered.')
class ComplaintForm(FlaskForm):
    category = SelectField('Main Category', choices=[
        ('', '-- Select Category --'),
        ('academics', 'Academics'),
        ('faculty', 'Faculty'),
        ('maintenance', 'Maintenance'),
        ('health_safety', 'Health & Safety'),
        ('general', 'General')
    ], validators=[DataRequired()])
    
    sub_topic = SelectField('Sub-topic', choices=[], validate_choice=False)
    subject_line = StringField('Subject Line', validators=[DataRequired()])
    description = TextAreaField('Complaint Details', validators=[DataRequired()])
    attachment = FileField('Attachment (optional)', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'png'], 'Allowed formats: PDF, DOC, JPG, PNG')
    ])
    submit = SubmitField('Submit')

class EditUserForm(FlaskForm):
    student_staff_number = StringField('Student/Staff Number', validators=[DataRequired(), Length(min=4, max=8)])
    is_staff = BooleanField('Is Staff')

class EditComplaintForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    sub_topic = StringField('Sub Topic', validators=[DataRequired()])
    subject_line = StringField('Subject Line', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    user_id = IntegerField('User ID', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved')])

class EditNotificationForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    is_read = BooleanField('Is Read')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    student_staff_number = db.Column(db.String(8), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_staff = db.Column(db.Boolean, default=False)
    # ... other fields ...

class AddComplaintForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    sub_topic = StringField('Sub Topic', validators=[DataRequired()])
    subject_line = StringField('Subject Line', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    user_id = IntegerField('User ID', validators=[DataRequired()])

class AddNotificationForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    is_read = BooleanField('Is Read')

class ComplaintFeedbackForm(FlaskForm):
    rating = SelectField(
        'How satisfied are you with the resolution of your complaint?',
        choices=[
            (5, 'Very Satisfied'),
            (4, 'Satisfied'),
            (3, 'Neutral'),
            (2, 'Unsatisfied'),
            (1, 'Very Unsatisfied')
        ],
        coerce=int,
        validators=[DataRequired()]
    )
    comments = TextAreaField('Additional Comments', validators=[Length(max=500)])
    submit = SubmitField('Submit Feedback')


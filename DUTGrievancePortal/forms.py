from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, TextAreaField  # Added TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
import re

class RegistrationForm(FlaskForm):
    email = StringField('University Email', validators=[
        DataRequired(), 
        Email(),
        Length(max=255)
    ])
    student_staff_number = StringField('Student/Staff Number', validators=[
        DataRequired(),
        Length(min=8, max=8)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if not email.data.endswith('@dut4life.ac.za'):
            raise ValidationError('You must use your university email address (@dut4life.ac.za)')
        
    def validate_student_staff_number(self, field):
        if not field.data.isdigit():
            raise ValidationError('Student/Staff number must contain only digits')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

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
    # ... rest of the form ...
    
    subject_line = StringField('Subject Line')
    description = TextAreaField('Complaint Details', validators=[DataRequired()])
    attachment = FileField('Attachment (optional)', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'png'], 'Allowed formats: PDF, DOC, JPG, PNG')
    ])
    submit = SubmitField('Submit')

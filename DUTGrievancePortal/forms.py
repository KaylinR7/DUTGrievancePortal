from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    student_staff_number = StringField('Student/Staff Number', 
                                     validators=[DataRequired(), Length(min=4, max=8)])
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

class AddUserForm(FlaskForm):
    student_staff_number = StringField('Student/Staff Number', validators=[DataRequired(), Length(min=4, max=8)])
    is_staff = BooleanField('Is Staff')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])

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


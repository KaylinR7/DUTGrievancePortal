from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from .extensions import db, login_manager  # Import from extensions.py
from .models import User, Complaint, Notification
from .forms import ComplaintForm, RegistrationForm, LoginForm
from datetime import datetime, timedelta
from .utils import generate_reference_id, create_notification
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash
from .models import User, Complaint, Notification  # Import your models
from .forms import AddUserForm, AddComplaintForm, AddNotificationForm  # You'll need to create these forms
from .extensions import db
from flask import render_template, request, redirect, url_for, flash
from .models import User, Complaint, Notification
from .forms import EditUserForm, EditComplaintForm, EditNotificationForm  # You'll need to create these forms
from flask import redirect, url_for, flash
from .models import User, Complaint, Notification
from .extensions import db
import os

# Create blueprints
main_bp = Blueprint('main', __name__)
staff_bp = Blueprint('staff', __name__, url_prefix='/staff')
admin_bp = Blueprint('admin', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor to inject notification count into all templates
@main_bp.context_processor
def inject_notification_count():
    if current_user.is_authenticated:
        notification_count = Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).count()
        return {'notification_count': notification_count}
    return {}

# Main routes
@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/welcome')
def welcome():
    return render_template('welcome.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.email == form.email.data) | 
            (User.student_staff_number == form.student_staff_number.data)
        ).first()
        
        if existing_user:
            flash('Email or Student/Staff number already registered', 'danger')
            return redirect(url_for('main.register'))
        
        # Automatically set is_staff based on the length of student_staff_number
        is_staff = len(form.student_staff_number.data) == 4  # Staff number is 4 digits
        
        user = User(
            email=form.email.data,
            student_staff_number=form.student_staff_number.data,
            is_staff=is_staff  # Set is_staff based on student_staff_number length
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            
            # Check if the email belongs to an admin
            if form.email.data.startswith('admin') and form.email.data.endswith('dut4life.ac.za') and len(form.email.data.split('@')[0]) == 11:
                return redirect(url_for('admin.admin_dashboard'))
            
            # Redirect based on the student/staff number length
            if len(user.student_staff_number) == 4:  # Staff (4 digits)
                return redirect(url_for('staff.staff_dashboard'))
            elif len(user.student_staff_number) == 8:  # Student (8 digits)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid student/staff number format', 'danger')
                return redirect(url_for('main.login'))
                
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)


@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.welcome'))

# Complaint management routes
@main_bp.route('/submit-complaint', methods=['GET', 'POST'])
@login_required
def submit_complaint():
    form = ComplaintForm()
    
    if form.validate_on_submit():
        ref_id = generate_reference_id(
            form.category.data,
            form.sub_topic.data if form.category.data != 'general' else None
        )
        
        # Handle file upload
        attachment_path = None
        if form.attachment.data:
            filename = secure_filename(f"{ref_id}_{form.attachment.data.filename}")
            save_path = os.path.join(current_app.root_path, 'static/uploads', filename)
            form.attachment.data.save(save_path)
            attachment_path = f"uploads/{filename}"
        
        new_complaint = Complaint(
            category=form.category.data,
            sub_topic=form.sub_topic.data if form.category.data != 'general' else None,
            subject_line=form.subject_line.data,
            description=form.description.data,
            reference_id=ref_id,
            attachment_path=attachment_path,
            user_id=current_user.id
        )
        
        db.session.add(new_complaint)
        db.session.commit()
        flash(f'Complaint submitted! Reference ID: {ref_id}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('complaint.html', form=form)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    now = datetime.utcnow()
    current_complaints = Complaint.query.filter_by(user_id=current_user.id, status='Pending').all()
    complaint_history = Complaint.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'dashboard.html',
        current_complaints=current_complaints,
        complaint_history=complaint_history,
        now=now,
        timedelta=timedelta
    )

@main_bp.route('/current-complaints')
@login_required
def current_complaints():
    now = datetime.utcnow()
    complaints = Complaint.query.filter_by(user_id=current_user.id, status='Pending').all()
    return render_template('current_complaints.html', complaints=complaints, now=now, timedelta=timedelta)

@main_bp.route('/complaint-history')
@login_required
def complaint_history():
    now = datetime.utcnow()
    complaints = Complaint.query.filter_by(user_id=current_user.id).all()
    return render_template('complaint_history.html', complaints=complaints, now=now, timedelta=timedelta)

# Notification management routes
@main_bp.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    notifications_query = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())
    paginated_notifications = notifications_query.paginate(page=page, per_page=per_page)
    
    return render_template(
        'notifications.html',
        notifications=paginated_notifications.items,
        page=page,
        total_pages=paginated_notifications.pages
    )

@main_bp.route('/mark-all-notifications-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
        .update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read', 'success')
    return redirect(url_for('main.notifications'))

@main_bp.route('/mark-notification-read/<int:id>', methods=['POST'])
@login_required
def mark_notification_read(id):
    notification = Notification.query.get_or_404(id)
    if notification.user_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('main.notifications'))
    
    notification.is_read = True
    db.session.commit()
    flash('Notification marked as read', 'success')
    return redirect(url_for('main.notifications'))

@main_bp.route('/delete-notification/<int:id>', methods=['POST'])
@login_required
def delete_notification(id):
    notification = Notification.query.get_or_404(id)
    if notification.user_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('main.notifications'))
    
    db.session.delete(notification)
    db.session.commit()
    flash('Notification deleted', 'success')
    return redirect(url_for('main.notifications'))

# Complaint resolution route
@main_bp.route('/respond-to-complaint/<int:complaint_id>', methods=['POST'])
@login_required
def main_respond_to_complaint(complaint_id):
    if not current_user.is_staff:
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('main.dashboard'))

    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.status = 'Resolved'
    db.session.commit()

    create_notification(
        complaint.user_id,
        f"Your complaint ({complaint.reference_id}) has been resolved."
    )
    flash('Complaint resolved successfully', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/view_complaint/<int:id>')  # Add <int:id> to the route to accept a complaint ID
@login_required
def view_complaint(id):
    # Fetch the complaint from the database using the provided ID
    complaint = Complaint.query.get_or_404(id)
    
    # Ensure the complaint belongs to the current user (or staff, if applicable)
    if complaint.user_id != current_user.id and not current_user.is_staff:
        flash('You do not have permission to view this complaint.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Calculate the deadline
    deadline = complaint.created_at + timedelta(hours=72)
    
    # Render the template with the complaint and deadline
    return render_template('view_complaint.html', complaint=complaint, deadline=deadline)

@main_bp.route('/faqs')
def faqs():
    return render_template('faqs.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@staff_bp.route('/dashboard')
@login_required
def staff_dashboard():
    if not current_user.is_staff:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get stats for the dashboard
    new_complaints = Complaint.query.filter_by(status='Pending').count()
    resolved_complaints = Complaint.query.filter_by(status='Resolved').count()
    in_progress_complaints = Complaint.query.filter_by(status='In Progress').count()
    
    # Get the first new complaint (if any)
    first_new_complaint = Complaint.query.filter_by(status='Pending').first()
    
    return render_template(
        'staff_dashboard.html',
        new_complaints=new_complaints,
        resolved_complaints=resolved_complaints,
        in_progress_complaints=in_progress_complaints,
        complaint=first_new_complaint  # Pass the first new complaint (may be None)
    )

@staff_bp.route('/complaints')
@login_required
def staff_complaints():
    if not current_user.is_staff:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    complaints = Complaint.query.filter_by(status='Pending').all()
    return render_template('staff_complaints.html', complaints=complaints)

@staff_bp.route('/history')
@login_required
def staff_history():
    if not current_user.is_staff:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    resolved_complaints = Complaint.query.filter_by(status='Resolved').all()
    return render_template('staff_history.html', complaints=resolved_complaints)


@staff_bp.route('/respond-to-complaint/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
def staff_respond_to_complaint(complaint_id):
    if not current_user.is_staff:
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('main.dashboard'))  # Redirect to staff dashboard if unauthorized

    complaint = Complaint.query.get_or_404(complaint_id)

    if request.method == 'POST':
        # Handle the form submission for responding to the complaint
        response = request.form.get('response')
        if response:
            complaint.status = 'Resolved'
            complaint.response = response
            db.session.commit()

            # Notify the student about the response
            create_notification(
                complaint.user_id,
                f"Your complaint ({complaint.reference_id}) has been resolved."
            )
            flash('Complaint resolved successfully', 'success')
            return redirect(url_for('staff.staff_complaints'))  # Redirect back to complaints list

    # For GET requests, render the response form
    return render_template('respond_to_complaint.html', complaint=complaint)



@staff_bp.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))



@admin_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not (current_user.email.startswith('admin') and current_user.email.endswith('dut4life.ac.za') and len(current_user.email.split('@')[0]) == 11):
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('admin_dashboard.html')

@admin_bp.route('/database')
def admin_database():
    # Query all users, complaints, and notifications with pagination
    page = request.args.get('page', 1, type=int)  # Get the current page number
    per_page = 10  # Number of items per page

    users = User.query.paginate(page=page, per_page=per_page)
    complaints = Complaint.query.paginate(page=page, per_page=per_page)
    notifications = Notification.query.paginate(page=page, per_page=per_page)

    return render_template(
        'admin_database.html',
        users=users,
        complaints=complaints,
        notifications=notifications
    )

# Add User
@admin_bp.route('/database/user/add', methods=['GET', 'POST'])
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            student_staff_number=form.student_staff_number.data,
            is_staff=form.is_staff.data
        )
        user.set_password(form.password.data)  # Set a default password
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('admin.admin_database'))
    return render_template('add_user.html', form=form)

# Add Complaint
@admin_bp.route('/database/complaint/add', methods=['GET', 'POST'])
def add_complaint():
    form = AddComplaintForm()
    if form.validate_on_submit():
        complaint = Complaint(
            category=form.category.data,
            sub_topic=form.sub_topic.data,
            subject_line=form.subject_line.data,
            description=form.description.data,
            user_id=form.user_id.data
        )
        db.session.add(complaint)
        db.session.commit()
        flash('Complaint added successfully!', 'success')
        return redirect(url_for('admin.admin_database'))
    return render_template('add_complaint.html', form=form)

# Add Notification
@admin_bp.route('/database/notification/add', methods=['GET', 'POST'])
def add_notification():
    form = AddNotificationForm()
    if form.validate_on_submit():
        notification = Notification(
            user_id=form.user_id.data,
            message=form.message.data,
            is_read=form.is_read.data
        )
        db.session.add(notification)
        db.session.commit()
        flash('Notification added successfully!', 'success')
        return redirect(url_for('admin.admin_database'))
    return render_template('add_notification.html', form=form)

# Edit User
@admin_bp.route('/database/user/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)
    form = EditUserForm(obj=user)  # Pre-populate the form with the user's data
    if form.validate_on_submit():
        form.populate_obj(user)  # Update the user object with form data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.admin_database'))
    return render_template('edit_user.html', form=form, user=user)

# Edit Complaint
@admin_bp.route('/database/complaint/edit/<int:id>', methods=['GET', 'POST'])
def edit_complaint(id):
    complaint = Complaint.query.get_or_404(id)
    form = EditComplaintForm(obj=complaint)  # Pre-populate the form with the complaint's data
    if form.validate_on_submit():
        form.populate_obj(complaint)  # Update the complaint object with form data
        db.session.commit()
        flash('Complaint updated successfully!', 'success')
        return redirect(url_for('admin.admin_database'))
    return render_template('edit_complaint.html', form=form, complaint=complaint)

# Edit Notification
@admin_bp.route('/database/notification/edit/<int:id>', methods=['GET', 'POST'])
def edit_notification(id):
    notification = Notification.query.get_or_404(id)
    form = EditNotificationForm(obj=notification)  # Pre-populate the form with the notification's data
    if form.validate_on_submit():
        form.populate_obj(notification)  # Update the notification object with form data
        db.session.commit()
        flash('Notification updated successfully!', 'success')
        return redirect(url_for('admin.admin_database'))
    return render_template('edit_notification.html', form=form, notification=notification)

# Delete User
@admin_bp.route('/database/user/delete/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.admin_database'))

# Delete Complaint
@admin_bp.route('/database/complaint/delete/<int:id>', methods=['POST'])
def delete_complaint(id):
    complaint = Complaint.query.get_or_404(id)
    db.session.delete(complaint)
    db.session.commit()
    flash('Complaint deleted successfully!', 'success')
    return redirect(url_for('admin.admin_database'))

# Delete Notification
@admin_bp.route('/database/notification/delete/<int:id>', methods=['POST'])
def delete_notification(id):
    notification = Notification.query.get_or_404(id)
    db.session.delete(notification)
    db.session.commit()
    flash('Notification deleted successfully!', 'success')
    return redirect(url_for('admin.admin_database'))






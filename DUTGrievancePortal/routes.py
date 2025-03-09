from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from .models import User, Complaint, Notification
from .forms import ComplaintForm, RegistrationForm, LoginForm
from . import db, login_manager
from datetime import datetime, timedelta
from .utils import generate_reference_id, create_notification
from werkzeug.utils import secure_filename
import os

main_bp = Blueprint('main', __name__)

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

# Authentication routes
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
            
        user = User(
            email=form.email.data,
            student_staff_number=form.student_staff_number.data
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
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
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
def respond_to_complaint(complaint_id):
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
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from .extensions import db, login_manager  
from .models import User, Complaint, Notification, ComplaintUpdate, Feedback
from .forms import ComplaintForm, LoginForm, ComplaintFeedbackForm, QuickStatusForm
from datetime import datetime, timedelta
from .utils import generate_reference_id, create_notification
from werkzeug.utils import secure_filename
import os

main_bp = Blueprint('main', __name__)
staff_bp = Blueprint('staff', __name__, url_prefix='/staff')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor for notification count
@main_bp.context_processor
def inject_notification_count():
    if current_user.is_authenticated:
        notification_count = Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).count()
        return {'notification_count': notification_count}
    return {}

# Home Page - Accessible to all
@main_bp.route('/')
def index():
    return render_template('index.html')

# Login/Logout Routes
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Always return to home after login

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(student_staff_number=form.student_staff_number.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))  # Go to home after login
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# Quick Status Update - Works for all user types
@main_bp.route('/quick-status', methods=['GET', 'POST'])
@login_required
def quick_status():
    form = QuickStatusForm()
    
    if form.validate_on_submit():
        complaint = Complaint.query.filter_by(reference_id=form.reference_id.data).first()
        
        if not complaint:
            flash('Complaint not found', 'danger')
        elif current_user.is_staff or current_user.is_admin:
            # Staff/Admin can update status
            complaint.status = form.status.data
            update = ComplaintUpdate(
                complaint_id=complaint.id,
                updated_by=f"{'Admin' if current_user.is_admin else 'Staff'} #{current_user.student_staff_number}",
                update_text=form.update_text.data
            )
            db.session.add(update)
            db.session.commit()
            
            # Notify student
            create_notification(
                complaint.user_id,
                f"Your complaint {complaint.reference_id} status updated to {form.status.data}"
            )
            flash('Status updated successfully', 'success')
        elif complaint.user_id == current_user.id:
            # Students can only view status
            flash(f"Current status: {complaint.status}", 'info')
        else:
            flash('You do not have permission to view this complaint', 'danger')
        
        return redirect(url_for('main.quick_status'))
    
    return render_template('quick_status.html', form=form)

# Student Routes
@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_staff or current_user.is_admin:
        return redirect(url_for('staff.staff_dashboard' if current_user.is_staff else 'admin.admin_dashboard'))
    
    complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.created_at.desc()).all()
    return render_template('student/dashboard.html', complaints=complaints)

@main_bp.route('/submit-complaint', methods=['GET', 'POST'])
@login_required
def submit_complaint():
    if current_user.is_staff or current_user.is_admin:
        return redirect(url_for('main.dashboard'))
    
    form = ComplaintForm()
    if form.validate_on_submit():
        ref_id = generate_reference_id(form.category.data, form.sub_topic.data)
        
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
            user_id=current_user.id,
            status='Pending'
        )
        
        db.session.add(new_complaint)
        db.session.commit()
        flash(f'Complaint submitted! Reference ID: {ref_id}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('student/submit_complaint.html', form=form)

# Staff Routes
@staff_bp.route('/dashboard')
@login_required
def staff_dashboard():
    if not current_user.is_staff and not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.dashboard'))
    
    pending = Complaint.query.filter_by(status='Pending').count()
    in_progress = Complaint.query.filter_by(status='In Progress').count()
    resolved = Complaint.query.filter_by(status='Resolved').count()
    reopened = Complaint.query.filter_by(status='Reopened').count()
    
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()
    
    return render_template('staff/dashboard.html',
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        reopened=reopened,
        recent_complaints=recent_complaints
    )

@staff_bp.route('/complaints')
@login_required
def staff_complaints():
    if not current_user.is_staff and not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.dashboard'))
    
    status_filter = request.args.get('status', 'Pending')
    complaints = Complaint.query.filter_by(status=status_filter).order_by(Complaint.created_at.desc()).all()
    return render_template('staff/complaints.html', complaints=complaints, status_filter=status_filter)

# Admin Routes
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.dashboard'))
    
    user_count = User.query.count()
    complaint_count = Complaint.query.count()
    active_complaints = Complaint.query.filter(Complaint.status.in_(['Pending', 'In Progress'])).count()
    
    return render_template('admin/dashboard.html',
        user_count=user_count,
        complaint_count=complaint_count,
        active_complaints=active_complaints
    )

@admin_bp.route('/manage-users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.order_by(User.student_staff_number).all()
    return render_template('admin/manage_users.html', users=users)

# Common Routes for All Users
@main_bp.route('/complaint/<reference_id>')
@login_required
def view_complaint(reference_id):
    complaint = Complaint.query.filter_by(reference_id=reference_id).first_or_404()
    
    # Authorization check
    if not (current_user.is_admin or current_user.is_staff or complaint.user_id == current_user.id):
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.dashboard'))
    
    updates = ComplaintUpdate.query.filter_by(complaint_id=complaint.id).order_by(ComplaintUpdate.update_time.desc()).all()
    feedback = Feedback.query.filter_by(complaint_id=complaint.id).first()
    
    return render_template('view_complaint.html',
        complaint=complaint,
        updates=updates,
        feedback=feedback,
        current_user=current_user
    )

@main_bp.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)

# Static Pages
@main_bp.route('/faqs')
def faqs():
    return render_template('static/faqs.html')

@main_bp.route('/contact')
def contact():
    return render_template('static/contact.html')

@main_bp.route('/about')
def about():
    return render_template('static/about.html')

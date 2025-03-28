from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from .extensions import db, login_manager  
from .models import User, Complaint, Notification
from .forms import ComplaintForm, LoginForm , RegistrationForm
from datetime import datetime, timedelta
from .utils import generate_reference_id, create_notification
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash
from .models import User, Complaint, Notification  
from .forms import AddUserForm, AddComplaintForm, AddNotificationForm  
from flask import render_template, request, redirect, url_for, flash
from .models import User, Complaint, Notification
from .forms import EditUserForm, EditComplaintForm, EditNotificationForm  
from flask import redirect, url_for, flash
from .models import User, Complaint, Notification
from .extensions import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session  # Added session
from .models import ComplaintUpdate
from .models import Feedback
from .forms import ComplaintFeedbackForm

import os


main_bp = Blueprint('main', __name__)
staff_bp = Blueprint('staff', __name__, url_prefix='/staff')
admin_bp = Blueprint('admin', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main_bp.context_processor
def inject_notification_count():
    if current_user.is_authenticated:
        notification_count = Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).count()
        return {'notification_count': notification_count}
    return {}

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        # Check user role and redirect accordingly
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.is_staff:
            return redirect(url_for('staff.staff_dashboard'))
        else:
            return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.is_staff:
            return redirect(url_for('staff.staff_dashboard'))
        else:
            return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(student_staff_number=form.student_staff_number.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))
            elif user.is_staff:
                return redirect(url_for('staff.staff_dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid student/staff number or password', 'danger')
    
    return render_template('login.html', form=form)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Students must register with email, staff/admin are created by admin
        if '@' not in form.email.data:
            flash('Students must register with email address', 'danger')
            return redirect(url_for('main.register'))
            
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('main.register'))
            
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            student_staff_number=form.student_staff_number.data,
            email=form.email.data,
            is_staff=False,
            is_admin=False
        )
        user.password = form.password.data
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)
    
    
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()  # ? Proper Flask-Login logout
    return redirect(url_for('main.login'))  # ? Use url_for



@main_bp.route('/submit-complaint', methods=['GET', 'POST'])
@login_required
def submit_complaint():
    form = ComplaintForm()
    
    if form.validate_on_submit():
        ref_id = generate_reference_id(
            form.category.data,
            form.sub_topic.data if form.category.data != 'general' else None
        )
        
     
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

@main_bp.route('/view_complaint/<int:id>')  
@login_required
def view_complaint(id):
   
    complaint = Complaint.query.get_or_404(id)
    
   
    if complaint.user_id != current_user.id and not current_user.is_staff:
        flash('You do not have permission to view this complaint.', 'danger')
        return redirect(url_for('main.dashboard'))
 
    deadline = complaint.created_at + timedelta(hours=72)
    
    
    return render_template('view_complaint.html', complaint=complaint, deadline=deadline)

@main_bp.route('/provide-feedback/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
def provide_feedback(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check if this complaint belongs to the current user
    if complaint.user_id != current_user.id:
        flash('You do not have permission to provide feedback for this complaint.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Check if feedback already exists
    existing_feedback = Feedback.query.filter_by(complaint_id=complaint_id, user_id=current_user.id).first()
    if existing_feedback:
        flash('You have already provided feedback for this complaint.', 'warning')
        return redirect(url_for('main.view_complaint', id=complaint_id))
    
    # Check if the complaint is in a state where feedback is appropriate
    if complaint.status not in ['Resolved', 'In Progress']:
        flash('This complaint is not yet ready for feedback.', 'warning')
        return redirect(url_for('main.view_complaint', id=complaint_id))
    
    form = ComplaintFeedbackForm()
    
    if form.validate_on_submit():
        # Create new feedback
        feedback = Feedback(
            complaint_id=complaint_id,
            user_id=current_user.id,
            rating=form.rating.data,
            comments=form.comments.data
        )
        
        db.session.add(feedback)
        
        # If rating is low (1 or 2), reopen the complaint
        if form.rating.data <= 2:
            complaint.status = 'Reopened'
            
            # Create notification for staff
            create_notification(
                complaint.user_id,  # This should ideally notify staff, but for now we'll use the same user
                f"Complaint {complaint.reference_id} has been reopened due to unsatisfactory resolution."
            )
            
            flash('Thank you for your feedback. Your complaint has been reopened for further review.', 'info')
        else:
            # For ratings 3-5, mark as fully resolved if not already
            if complaint.status != 'Resolved':
                complaint.status = 'Resolved'
            
            flash('Thank you for your feedback. We appreciate your input.', 'success')
        
        db.session.commit()
        return redirect(url_for('main.view_complaint', id=complaint_id))
    
    return render_template('provide_feedback.html', form=form, complaint=complaint)

# Add this route to handle reopened complaints
@staff_bp.route('/reopened-complaints')
@login_required
def reopened_complaints():
    if not current_user.is_staff:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    complaints = Complaint.query.filter_by(status='Reopened').all()
    return render_template('staff_reopened_complaints.html', complaints=complaints)



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
    
    # Get counts for all statuses
    new_complaints = Complaint.query.filter_by(status='Pending').count()
    resolved_complaints = Complaint.query.filter_by(status='Resolved').count()
    in_progress_complaints = Complaint.query.filter_by(status='In Progress').count()
    reopened_complaints = Complaint.query.filter_by(status='Reopened').count()

    # Get recent complaints (last 5 pending or in progress)
    recent_complaints = Complaint.query.filter(
        Complaint.status.in_(['Pending', 'In Progress'])
    ).order_by(Complaint.created_at.desc()).limit(5).all()

    # Get reopened complaints
    reopened_complaints_list = Complaint.query.filter_by(status='Reopened').order_by(Complaint.created_at.desc()).all()

    return render_template(
        'staff_dashboard.html',
        new_complaints=new_complaints,
        resolved_complaints=resolved_complaints,
        in_progress_complaints=in_progress_complaints,
        reopened_complaints=reopened_complaints,
        recent_complaints=recent_complaints,
        reopened_complaints_list=reopened_complaints_list  # Add this
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




# Replace the conflicting route with this one (use a different name)

@staff_bp.route('/complaints-needing-attention')  # Changed from '/reopened-complaints'
@login_required
def complaints_needing_attention():  # Changed from 'reopened_complaints'
    if not current_user.is_staff:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    complaints = Complaint.query.filter_by(status='Reopened').all()
    return render_template('staff_complaints_needing_attention.html', complaints=complaints)  # Changed template name

@staff_bp.route('/view_complaint/<int:complaint_id>')  # <-- Note complaint_id parameter
@login_required
def staff_view_complaint(complaint_id):  # <-- Match parameter name
    if not current_user.is_staff:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.dashboard'))

    complaint = Complaint.query.get_or_404(complaint_id)
    updates = ComplaintUpdate.query.filter_by(complaint_id=complaint.id).order_by(ComplaintUpdate.update_time.desc()).all()
    
    return render_template(
        'staff_view_complaint.html', 
        complaint=complaint,
        updates=updates
    )



# Update your existing staff_respond_to_complaint route

@staff_bp.route('/respond-to-complaint/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
def staff_respond_to_complaint(complaint_id):
    if not current_user.is_staff:
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('main.dashboard'))  

    complaint = Complaint.query.get_or_404(complaint_id)

    if request.method == 'POST':
        response = request.form.get('response')
        resolution_type = request.form.get('resolution_type')
        
        if response:
            # Add a complaint update
            update = ComplaintUpdate(
                complaint_id=complaint.id,
                updated_by=f"Staff #{current_user.student_staff_number}",
                update_text=response
            )
            db.session.add(update)
            
            # Change status based on resolution type
            if resolution_type == 'resolve':
                complaint.status = 'Resolved'
                message = f"Your complaint ({complaint.reference_id}) has been resolved. Please provide feedback on the resolution."
            else:
                complaint.status = 'In Progress'
                message = f"There's an update on your complaint ({complaint.reference_id}). Please check your dashboard."
            
            # Create notification for the student
            create_notification(
                complaint.user_id,
                message
            )
            
            db.session.commit()
            flash('Response submitted successfully', 'success')
            return redirect(url_for('staff.staff_complaints'))  

    # Get all updates for this complaint
    updates = ComplaintUpdate.query.filter_by(complaint_id=complaint.id).order_by(ComplaintUpdate.update_time.desc()).all()
    
    return render_template('respond_to_complaint.html', complaint=complaint, updates=updates)




@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))



# Replace the old email-based admin check with this
def is_admin(user):
    return user.is_admin

@admin_bp.route('/dashboard')
@login_required

def admin_dashboard():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.dashboard'))
    return render_template('admin_dashboard.html')

@admin_bp.route('/database')
def admin_database():
   
    page = request.args.get('page', 1, type=int)  
    per_page = 10  

    users = User.query.paginate(page=page, per_page=per_page)
    complaints = Complaint.query.paginate(page=page, per_page=per_page)
    notifications = Notification.query.paginate(page=page, per_page=per_page)

    return render_template(
        'admin_database.html',
        users=users,
        complaints=complaints,
        notifications=notifications
    )


# In your routes.py (add_user route)
@admin_bp.route('/admin/database/user/add', methods=['GET', 'POST'])
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        new_user = User(
            student_staff_number=form.student_staff_number.data,
            email=form.email.data,  # Missing in your implementation
            first_name=form.first_name.data,  # Missing in your implementation
            last_name=form.last_name.data,  # Missing in your implementation
            password=form.password.data,  # This should use the password setter
            is_staff=form.is_staff.data,
            is_admin=form.is_admin.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('admin.admin_database'))
    return render_template('add_user.html', form=form)

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


@admin_bp.route('/database/user/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)
    form = EditUserForm(obj=user)
    
    if form.validate_on_submit():
        # Manually update fields instead of using populate_obj() 
        # to handle password separately
        user.student_staff_number = form.student_staff_number.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.is_staff = form.is_staff.data
        user.is_admin = form.is_admin.data
        
        # Only update password if a new one was entered
        if form.password.data:  # Check if password field is not empty
            user.password = form.password.data  # This uses the password setter
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.admin_database'))
    
    return render_template('edit_user.html', form=form, user=user)


@admin_bp.route('/database/complaint/edit/<int:id>', methods=['GET', 'POST'])
def edit_complaint(id):
    complaint = Complaint.query.get_or_404(id)
    form = EditComplaintForm(obj=complaint) 
    if form.validate_on_submit():
        form.populate_obj(complaint)  
        db.session.commit()
        flash('Complaint updated successfully!', 'success')
        return redirect(url_for('admin.admin_database'))
    return render_template('edit_complaint.html', form=form, complaint=complaint)


@admin_bp.route('/database/notification/edit/<int:id>', methods=['GET', 'POST'])
def edit_notification(id):
    notification = Notification.query.get_or_404(id)
    form = EditNotificationForm(obj=notification)  
    if form.validate_on_submit():
        form.populate_obj(notification)  
        db.session.commit()
        flash('Notification updated successfully!', 'success')
        return redirect(url_for('admin.admin_database'))
    return render_template('edit_notification.html', form=form, notification=notification)


@admin_bp.route('/database/user/delete/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.admin_database'))

@admin_bp.route('/database/complaint/delete/<int:id>', methods=['POST'])
def delete_complaint(id):
    complaint = Complaint.query.get_or_404(id)
    db.session.delete(complaint)
    db.session.commit()
    flash('Complaint deleted successfully!', 'success')
    return redirect(url_for('admin.admin_database'))


@admin_bp.route('/database/notification/delete/<int:id>', methods=['POST'])
def delete_notification(id):
    notification = Notification.query.get_or_404(id)
    db.session.delete(notification)
    db.session.commit()
    flash('Notification deleted successfully!', 'success')
    return redirect(url_for('admin.admin_database'))





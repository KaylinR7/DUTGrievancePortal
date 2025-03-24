from datetime import datetime
from flask import current_app
from .extensions import db
import secrets

def generate_reference_id(category, sub_topic=None):
    # Generate unique base
    timestamp = datetime.now().strftime("%m%d%H%M")  # MonthDayHourMinute
    random_part = secrets.token_hex(2).upper()  # 4-character random string
    
    # Create category code
    category_code = category[:3].upper()
    
    # Create sub-topic code if exists
    sub_code = ""
    if sub_topic:
        sub_code = sub_topic.split("_")[-1][:3].upper()
    
    # Construct reference ID
    ref_id = f"{category_code}-{sub_code}{timestamp}-{random_part}"
    
    # Ensure uniqueness
    from .models import Complaint
    while Complaint.query.filter_by(reference_id=ref_id).first():
        random_part = secrets.token_hex(2).upper()
        ref_id = f"{category_code}-{sub_code}{timestamp}-{random_part}"
    
    return ref_id

def create_notification(user_id, message):
    """Create and save a new notification for a user"""
    try:
        notification = Notification(
            user_id=user_id,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Notification creation failed: {str(e)}")
        return False

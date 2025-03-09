# DUTGrievancePortal/utils.py
import uuid
from datetime import datetime
from .models import Notification, db

def generate_reference_id(category, sub_topic=None):
    category_map = {
        'academics': 'ACA',
        'faculty': 'FAC',
        'maintenance': 'MNT',
        'health_safety': 'HLS',
        'general': 'GEN'
    }
    
    sub_topic_map = {
        'academics_registration': 'REG',
        'academics_results': 'RES',
        'faculty_teaching': 'TCH',
        'faculty_resources': 'RES',
        'maintenance_cleaning': 'CLN',
        'maintenance_infrastructure': 'INF',
        'health_safety_emergency': 'EMG',
        'health_safety_facilities': 'FAC'
    }
    
    prefix = category_map.get(category, 'GEN')
    sub_code = sub_topic_map.get(sub_topic, '')[:3] if sub_topic else ''
    unique_id = str(uuid.uuid4().hex)[:8].upper()
    timestamp = datetime.now().strftime('%H%M')
    
    return f"{prefix}-{sub_code}{timestamp}-{unique_id[-4:]}"

def create_notification(user_id, message):
    notification = Notification(
        user_id=user_id,
        message=message,
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()
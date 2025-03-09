from DUTGrievancePortal import create_app, db
from DUTGrievancePortal.models import Complaint, User  # Add User model

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Database tables created!")
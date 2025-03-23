from DUTGrievancePortal import create_app, db
from DUTGrievancePortal.models import User

# Initialize Flask app
app = create_app()

# Create admin user within app context
with app.app_context():
    # Create admin user
    admin = User(
        student_staff_number='ADMIN123',  # Change to desired admin ID
        is_admin=True,
        is_staff=True
    )
    admin.password = '123456789'  # Set this password
    
    # Add to database
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user {admin.student_staff_number} created successfully!")

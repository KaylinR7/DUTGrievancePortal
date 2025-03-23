from DUTGrievancePortal import create_app
from DUTGrievancePortal.extensions import db  

app = create_app()

with app.app_context():
    db.create_all()
from extensions import db
from datetime import datetime

class Drive(db.Model):
    __tablename__ = 'drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    drive_name = db.Column(db.String(150), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text)
    eligibility_branch = db.Column(db.String(200))
    eligibility_cgpa = db.Column(db.Float, default=0.0)
    eligibility_year = db.Column(db.Integer)
    salary = db.Column(db.String(100))
    location = db.Column(db.String(100))
    application_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='drive', lazy=True, cascade='all, delete-orphan')
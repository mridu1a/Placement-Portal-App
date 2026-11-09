from extensions import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    hr_contact = db.Column(db.String(100))
    description = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='company')
    drives = db.relationship('Drive', backref='company', lazy=True, cascade='all, delete-orphan')
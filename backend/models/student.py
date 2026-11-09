from extensions import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    branch = db.Column(db.String(100))
    year = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    skills = db.Column(db.Text)
    resume_path = db.Column(db.String(300))
    phone = db.Column(db.String(20))
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='student')
    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')
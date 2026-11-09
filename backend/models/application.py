from extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id', ondelete='CASCADE'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='applied')  # 'applied', 'shortlisted', 'selected', 'rejected'
    interview_date = db.Column(db.DateTime, nullable=True)
    feedback = db.Column(db.Text, nullable=True)

    # Prevent duplicate applications
    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),
    )
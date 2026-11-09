from celery import Celery
from datetime import datetime, timedelta
import csv
import io
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Standalone celery instance
celery_app = Celery('tasks', broker='redis://127.0.0.1:6379/0', backend='redis://127.0.0.1:6379/0')

@celery_app.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    from app import app, mail
    from flask_mail import Message
    from models import Student, Drive, Application, User
    from extensions import db

    with app.app_context():
        upcoming = Drive.query.filter(
            Drive.status == 'approved',
            Drive.application_deadline >= datetime.utcnow(),
            Drive.application_deadline <= datetime.utcnow() + timedelta(days=3)
        ).all()

        for drive in upcoming:
            applied_subquery = db.session.query(Application.student_id).filter(Application.drive_id == drive.id).subquery()
            students_to_remind = db.session.query(Student, User.email).join(
                User, Student.user_id == User.id
            ).filter(~Student.id.in_(applied_subquery)).all()

            for student, email in students_to_remind:
                if email:
                    try:
                        msg = Message(
                            subject=f'Reminder: {drive.drive_name} deadline is approaching!',
                            recipients=[email],
                            body=f'''
Hi {student.full_name},

This is a reminder that the placement drive "{drive.drive_name}" has a deadline on {drive.application_deadline.strftime("%d %B %Y")}.

Don't miss out! Log in to apply now.

Placement Portal Team
                            '''
                        )
                        mail.send(msg)
                    except Exception as e:
                        print(f"Failed to send email to {email}: {e}")

    return 'Daily reminders sent!'


@celery_app.task(name='tasks.send_monthly_report')
def send_monthly_report():
    from app import app, mail
    from flask_mail import Message
    from models import Student, Company, Drive, Application, User

    with app.app_context():
        now = datetime.utcnow()
        first_day = now.replace(day=1, hour=0, minute=0, second=0)
        last_month = first_day - timedelta(days=1)
        month_start = last_month.replace(day=1)

        total_drives = Drive.query.filter(
            Drive.created_at >= month_start,
            Drive.created_at < first_day
        ).count()

        total_applications = Application.query.filter(
            Application.application_date >= month_start,
            Application.application_date < first_day
        ).count()

        total_selected = Application.query.filter(
            Application.application_date >= month_start,
            Application.application_date < first_day,
            Application.status == 'selected'
        ).count()

        html = f'''
        <html>
        <body style="font-family: Arial; padding: 20px; background: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h1 style="color: #f97316;">📊 Monthly Placement Report</h1>
                <h3 style="color: #666;">Month: {last_month.strftime("%B %Y")}</h3>
                <hr/>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f97316; color: white;">
                        <th style="padding: 12px;">Metric</th>
                        <th style="padding: 12px;">Count</th>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;">Total Drives Conducted</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{total_drives}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;">Total Applications</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{total_applications}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;">Students Selected</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{total_selected}</td>
                    </tr>
                </table>
                <p style="color: #999; margin-top: 20px;">Generated on {now.strftime("%d %B %Y")}</p>
            </div>
        </body>
        </html>
        '''

        admin = User.query.filter_by(role='admin').first()
        if admin:
            try:
                msg = Message(
                    subject=f'Monthly Placement Report - {last_month.strftime("%B %Y")}',
                    recipients=[admin.email],
                    html=html
                )
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send monthly report: {e}")

    return 'Monthly report sent!'


@celery_app.task(name='tasks.export_applications_csv')
def export_applications_csv(student_id):
    from app import app, mail
    from flask_mail import Message
    from models import Student, Drive, Application, Company, User
    from extensions import db

    with app.app_context():
        student = Student.query.get(student_id)
        if not student:
            return 'Student not found'
        
        user = User.query.get(student.user_id)
        applications_data = db.session.query(
            Application, Drive, Company.company_name
        ).outerjoin(Drive, Application.drive_id == Drive.id)\
         .outerjoin(Company, Drive.company_id == Company.id)\
         .filter(Application.student_id == student_id).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student ID', 'Student Name', 'Company', 'Drive', 'Job Title', 'Status', 'Applied On'])

        for a, drive, company_name in applications_data:
            writer.writerow([
                student.id,
                student.full_name,
                company_name if company_name else '',
                drive.drive_name if drive else '',
                drive.job_title if drive else '',
                a.status,
                a.application_date.strftime('%Y-%m-%d')
            ])

        csv_content = output.getvalue()

        if user and user.email:
            try:
                msg = Message(
                    subject='Your Application History - CSV Export',
                    recipients=[user.email],
                    body='Please find your application history attached.',
                )
                msg.attach(
                    'applications.csv',
                    'text/csv',
                    csv_content
                )
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send CSV: {e}")

    return 'CSV exported and sent!'
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models import User, Company, Drive, Application, Student
from datetime import datetime
from sqlalchemy import func

company_bp = Blueprint('company', __name__)

# ─── Helper: Check if current user is company ─────────────────────
def get_company_from_token():
    claims = get_jwt()
    if claims.get('role') != 'company':
        return None, jsonify({'message': 'Company access required'}), 403
    user_id = int(get_jwt_identity())
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return None, jsonify({'message': 'Company profile not found'}), 404
    if company.approval_status != 'approved':
        return None, jsonify({'message': 'Your company is not approved yet'}), 403
    if company.is_blacklisted:
        return None, jsonify({'message': 'Your company has been blacklisted'}), 403
    return company, None, None

# ─── COMPANY DASHBOARD ────────────────────────────────────────────
@company_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    company, err, code = get_company_from_token()
    if err:
        return err, code

    drive_data_query = db.session.query(
        Drive,
        func.count(Application.id).label('app_count')
    ).outerjoin(Application, Drive.id == Application.drive_id)\
     .filter(Drive.company_id == company.id)\
     .group_by(Drive.id).all()

    drive_data = []
    for d, app_count in drive_data_query:
        drive_data.append({
            'id': d.id,
            'drive_name': d.drive_name,
            'job_title': d.job_title,
            'status': d.status,
            'application_count': app_count,
            'application_deadline': d.application_deadline.isoformat() if d.application_deadline else None
        })

    return jsonify({
        'company_name': company.company_name,
        'industry': company.industry,
        'location': company.location,
        'drives': drive_data
    }), 200

# ─── CREATE DRIVE ─────────────────────────────────────────────────
@company_bp.route('/drives', methods=['POST'])
@jwt_required()
def create_drive():
    company, err, code = get_company_from_token()
    if err:
        return err, code

    data = request.get_json()

    if not data.get('drive_name') or not data.get('job_title'):
        return jsonify({'message': 'Drive name and job title are required'}), 400

    deadline = None
    if data.get('application_deadline'):
        deadline = datetime.fromisoformat(data['application_deadline'])

    drive = Drive(
        company_id=company.id,
        drive_name=data['drive_name'],
        job_title=data['job_title'],
        job_description=data.get('job_description', ''),
        eligibility_branch=data.get('eligibility_branch', ''),
        eligibility_cgpa=data.get('eligibility_cgpa', 0.0),
        eligibility_year=data.get('eligibility_year', None),
        salary=data.get('salary', ''),
        location=data.get('location', ''),
        application_deadline=deadline,
        status='pending'
    )
    db.session.add(drive)
    db.session.commit()
    return jsonify({'message': 'Drive created successfully! Waiting for admin approval.'}), 201

# ─── VIEW DRIVE APPLICATIONS ──────────────────────────────────────
@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@jwt_required()
def get_drive_applications(drive_id):
    company, err, code = get_company_from_token()
    if err:
        return err, code

    drive = Drive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    applications_data = db.session.query(Application, Student).join(
        Student, Application.student_id == Student.id
    ).filter(Application.drive_id == drive.id).all()

    result = []
    for a, student in applications_data:
        result.append({
            'application_id': a.id,
            'student_id': student.id,
            'student_name': student.full_name,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'skills': student.skills,
            'resume_path': student.resume_path,
            'status': a.status,
            'application_date': a.application_date.isoformat(),
            'interview_date': a.interview_date.isoformat() if a.interview_date else None,
            'feedback': a.feedback
        })
    return jsonify(result), 200

# ─── UPDATE APPLICATION STATUS ────────────────────────────────────
@company_bp.route('/applications/<int:application_id>', methods=['PUT'])
@jwt_required()
def update_application(application_id):
    company, err, code = get_company_from_token()
    if err:
        return err, code

    application = Application.query.get_or_404(application_id)
    drive = Drive.query.filter_by(id=application.drive_id, company_id=company.id).first_or_404()

    data = request.get_json()
    application.status = data.get('status', application.status)
    application.feedback = data.get('feedback', application.feedback)

    if data.get('interview_date'):
        application.interview_date = datetime.fromisoformat(data['interview_date'])

    db.session.commit()
    return jsonify({'message': 'Application updated successfully'}), 200

# ─── CLOSE DRIVE ──────────────────────────────────────────────────
@company_bp.route('/drives/<int:drive_id>/close', methods=['PUT'])
@jwt_required()
def close_drive(drive_id):
    company, err, code = get_company_from_token()
    if err:
        return err, code

    drive = Drive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    drive.status = 'closed'
    db.session.commit()
    return jsonify({'message': 'Drive closed successfully'}), 200

# ─── VIEW COMPANY PROFILE ─────────────────────────────────────────
@company_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    company, err, code = get_company_from_token()
    if err:
        return err, code

    return jsonify({
        'company_name': company.company_name,
        'industry': company.industry,
        'location': company.location,
        'website': company.website,
        'hr_contact': company.hr_contact,
        'description': company.description,
        'approval_status': company.approval_status
    }), 200

# ─── UPDATE COMPANY PROFILE ───────────────────────────────────────
@company_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    company, err, code = get_company_from_token()
    if err:
        return err, code

    data = request.get_json()
    company.company_name = data.get('company_name', company.company_name)
    company.industry = data.get('industry', company.industry)
    company.location = data.get('location', company.location)
    company.website = data.get('website', company.website)
    company.hr_contact = data.get('hr_contact', company.hr_contact)
    company.description = data.get('description', company.description)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Company, Student, Drive, Application
from sqlalchemy import func, case

admin_bp = Blueprint('admin', __name__)

# ─── Helper: Check if current user is admin ───────────────────────
from flask_jwt_extended import get_jwt

def admin_required():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return False
    return True

# ─── DASHBOARD STATS ──────────────────────────────────────────────
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = Drive.query.count()
    total_applications = Application.query.count()
    pending_companies = Company.query.filter_by(approval_status='pending').count()
    pending_drives = Drive.query.filter_by(status='pending').count()

    return jsonify({
        'total_students': total_students,
        'total_companies': total_companies,
        'total_drives': total_drives,
        'total_applications': total_applications,
        'pending_companies': pending_companies,
        'pending_drives': pending_drives
    }), 200

# ─── VIEW ALL COMPANIES ───────────────────────────────────────────
@admin_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    from cache import get_cache, set_cache
    search = request.args.get('search', '').strip()

    # Only cache when no search query
    if not search:
        cached = get_cache('admin_companies')
        if cached:
            return jsonify(cached), 200

    query = db.session.query(Company, User.email).outerjoin(User, Company.user_id == User.id)
    if search:
        query = query.filter(Company.company_name.ilike(f'%{search}%'))

    companies_data = query.all()
    result = []
    for c, email in companies_data:
        result.append({
            'id': c.id,
            'company_name': c.company_name,
            'industry': c.industry,
            'location': c.location,
            'website': c.website,
            'hr_contact': c.hr_contact,
            'description': c.description or '',
            'approval_status': c.approval_status,
            'is_blacklisted': c.is_blacklisted,
            'email': email or ''
        })

    if not search:
        set_cache('admin_companies', result, expiry=120)

    return jsonify(result), 200

# ─── APPROVE / REJECT COMPANY ─────────────────────────────────────
@admin_bp.route('/companies/<int:company_id>/approval', methods=['PUT'])
@jwt_required()
def update_company_approval(company_id):
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    data = request.get_json()
    company = Company.query.get_or_404(company_id)
    company.approval_status = data.get('status', company.approval_status)
    db.session.commit()
    
    # Clear cache
    from cache import delete_cache
    delete_cache('admin_companies')

    return jsonify({'message': f'Company status updated to {company.approval_status}'}), 200
    

# ─── BLACKLIST / ACTIVATE COMPANY ────────────────────────────────
@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['PUT'])
@jwt_required()
def blacklist_company(company_id):
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    company = Company.query.get_or_404(company_id)
    user = User.query.get(company.user_id)
    company.is_blacklisted = not company.is_blacklisted
    user.is_active = not company.is_blacklisted

    # If blacklisting, close all their drives
    if company.is_blacklisted:
        drives = Drive.query.filter_by(company_id=company.id).all()
        for drive in drives:
            drive.status = 'closed'
    db.session.commit()
    # Clear all student dashboard caches
    from cache import clear_pattern
    clear_pattern('student_dashboard_*')
    
    from cache import delete_cache
    delete_cache('admin_companies')
    status = 'blacklisted' if company.is_blacklisted else 'activated'
    return jsonify({'message': f'Company {status} successfully'}), 200

# ─── VIEW ALL STUDENTS ────────────────────────────────────────────
@admin_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    search = request.args.get('search', '').strip()
    query = db.session.query(Student, User.email).outerjoin(User, Student.user_id == User.id)

    if search:
        query = query.filter(Student.full_name.ilike(f'%{search}%'))

    students_data = query.all()
    result = []
    for s, email in students_data:
        result.append({
            'id': s.id,
            'full_name': s.full_name,
            'branch': s.branch,
            'year': s.year,
            'cgpa': s.cgpa,
            'skills': s.skills,
            'phone': s.phone,
            'is_blacklisted': s.is_blacklisted,
            'email': email or ''
        })
    return jsonify(result), 200

# ─── BLACKLIST / ACTIVATE STUDENT ────────────────────────────────
@admin_bp.route('/students/<int:student_id>/blacklist', methods=['PUT'])
@jwt_required()
def blacklist_student(student_id):
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    student = Student.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    student.is_blacklisted = not student.is_blacklisted
    user.is_active = not student.is_blacklisted
    db.session.commit()
    status = 'blacklisted' if student.is_blacklisted else 'activated'
    return jsonify({'message': f'Student {status} successfully'}), 200

# ─── VIEW ALL DRIVES ──────────────────────────────────────────────
@admin_bp.route('/drives', methods=['GET'])
@jwt_required()
def get_drives():
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    drives_data = db.session.query(
        Drive, 
        Company.company_name,
        func.count(Application.id).label('applied_count')
    ).outerjoin(Company, Drive.company_id == Company.id)\
     .outerjoin(Application, Drive.id == Application.drive_id)\
     .group_by(Drive.id, Company.id).all()
    result = []
    for d, company_name, applied_count in drives_data:
        result.append({
            'id': d.id,
            'drive_name': d.drive_name if d.drive_name else 'Unnamed Drive',
            'job_title': d.job_title,
            'job_description': d.job_description or '',
            'salary': d.salary or '',
            'location': d.location or '',
            'company_name': company_name if company_name else 'Unknown',
            'status': d.status,
            'application_deadline': d.application_deadline.isoformat() if d.application_deadline else None,
            'eligibility_cgpa': d.eligibility_cgpa,
            'eligibility_branch': d.eligibility_branch,
            'applied_count': applied_count
        })
    return jsonify(result), 200

# ─── APPROVE / REJECT DRIVE ───────────────────────────────────────
@admin_bp.route('/drives/<int:drive_id>/approval', methods=['PUT'])
@jwt_required()
def update_drive_approval(drive_id):
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    data = request.get_json()
    drive = Drive.query.get_or_404(drive_id)
    drive.status = data.get('status', drive.status)
    db.session.commit()

    # Clear student dashboard caches so new approved drives show up
    from cache import clear_pattern
    clear_pattern('student_dashboard_*')

    return jsonify({'message': f'Drive status updated to {drive.status}'}), 200
# ─── VIEW ALL APPLICATIONS ────────────────────────────────────────
@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    applications_data = db.session.query(
        Application,
        Student.full_name.label('student_name'),
        Student.branch.label('branch'),
        Drive.drive_name,
        Company.company_name
    ).outerjoin(Student, Application.student_id == Student.id)\
     .outerjoin(Drive, Application.drive_id == Drive.id)\
     .outerjoin(Company, Drive.company_id == Company.id).all()

    result = []
    for a, student_name, branch, drive_name, company_name in applications_data:
        result.append({
            'id': a.id,
            'student_id': a.student_id,
            'student_name': student_name or 'Unknown',
            'branch': branch or 'Computer Science',
            'drive_name': drive_name or 'Unknown',
            'company_name': company_name or 'Unknown',
            'status': a.status,
            'application_date': a.application_date.isoformat()
        })
    return jsonify(result), 200

@admin_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@jwt_required()
def delete_company(company_id):
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    company = Company.query.get_or_404(company_id)
    user = User.query.get(company.user_id)

    # Delete company and user. Cascades will delete associated drives and applications.
    db.session.delete(company)
    if user:
        db.session.delete(user)
    db.session.commit()

    from cache import delete_cache, clear_pattern
    delete_cache('admin_companies')
    clear_pattern('student_dashboard_*')
    return jsonify({'message': 'Company deleted successfully'}), 200

@admin_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    if not admin_required():
        return jsonify({'message': 'Admin access required'}), 403

    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = Drive.query.count()

    # Aggregate Application stats in one query
    app_counts = db.session.query(
        func.count(Application.id).label('total'),
        func.sum(case((Application.status == 'selected', 1), else_=0)).label('selected'),
        func.sum(case((Application.status == 'shortlisted', 1), else_=0)).label('shortlisted'),
        func.sum(case((Application.status == 'rejected', 1), else_=0)).label('rejected')
    ).first()

    total_applications = app_counts.total or 0
    total_selected = int(app_counts.selected or 0)
    total_shortlisted = int(app_counts.shortlisted or 0)
    total_rejected = int(app_counts.rejected or 0)
    total_applied = total_applications

    placement_rate = (
        round((total_selected / total_applications) * 100, 1)
        if total_applications > 0
        else 0.0
    )

    # Fetch all drive stats in one query
    drive_data = db.session.query(
        Drive.drive_name,
        Drive.job_title,
        Drive.status,
        Company.company_name,
        func.count(Application.id).label('total_apps'),
        func.sum(case((Application.status == 'selected', 1), else_=0)).label('selected_apps')
    ).outerjoin(Company, Drive.company_id == Company.id)\
     .outerjoin(Application, Drive.id == Application.drive_id)\
     .group_by(Drive.id, Company.id).all()

    drive_stats = []
    for drive_name, job_title, status, company_name, total_apps, selected_apps in drive_data:
        drive_stats.append({
            'drive_name': drive_name,
            'company_name': company_name or '',
            'job_title': job_title,
            'total_applications': total_apps,
            'selected': int(selected_apps or 0),
            'status': status
        })

    return jsonify({
        'total_students': total_students,
        'total_companies': total_companies,
        'total_drives': total_drives,
        'total_applications': total_applications,
        'total_selected': total_selected,
        'total_shortlisted': total_shortlisted,
        'total_rejected': total_rejected,
        'total_applied': total_applied,
        'placement_rate': placement_rate,
        'drive_stats': drive_stats
    }), 200
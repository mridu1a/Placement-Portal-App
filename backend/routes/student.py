from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models import User, Student, Drive, Application, Company
from datetime import datetime

student_bp = Blueprint('student', __name__)

# ─── Helper: Get student from token ───────────────────────────────
def get_student_from_token():
    claims = get_jwt()
    if claims.get('role') != 'student':
        return None, jsonify({'message': 'Student access required'}), 403
    user_id = int(get_jwt_identity())
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return None, jsonify({'message': 'Student profile not found'}), 404
    if student.is_blacklisted:
        return None, jsonify({'message': 'Your account has been blacklisted'}), 403
    return student, None, None

# ─── STUDENT DASHBOARD ────────────────────────────────────────────
@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    student, err, code = get_student_from_token()
    if err:
        return err, code

    # Try cache first
    from cache import get_cache, set_cache
    cache_key = f'student_dashboard_{student.id}'
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached), 200

    # Get all approved drives and join with Company & Student's Application
    drives_data = db.session.query(
        Drive,
        Company.company_name,
        Application.id.label('applied_id')
    ).outerjoin(Company, Drive.company_id == Company.id)\
     .outerjoin(Application, (Drive.id == Application.drive_id) & (Application.student_id == student.id))\
     .filter(Drive.status == 'approved').all()

    drive_list = []
    for d, company_name, applied_id in drives_data:
        drive_list.append({
            'id': d.id,
            'drive_name': d.drive_name,
            'job_title': d.job_title,
            'company_name': company_name or '',
            'location': d.location,
            'salary': d.salary,
            'eligibility_branch': d.eligibility_branch,
            'eligibility_cgpa': d.eligibility_cgpa,
            'eligibility_year': d.eligibility_year,
            'application_deadline': d.application_deadline.isoformat() if d.application_deadline else None,
            'already_applied': bool(applied_id)
        })

    result = {
        'student_name': student.full_name,
        'branch': student.branch,
        'cgpa': student.cgpa,
        'year': student.year,
        'drives': drive_list
    }

    # Save to cache for 5 minutes
    set_cache(cache_key, result, expiry=300)
    return jsonify(result), 200

# ─── VIEW & UPDATE PROFILE ────────────────────────────────────────
@student_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    student, err, code = get_student_from_token()
    if err:
        return err, code

    return jsonify({
        'full_name': student.full_name,
        'branch': student.branch,
        'year': student.year,
        'cgpa': student.cgpa,
        'skills': student.skills,
        'phone': student.phone,
        'resume_path': student.resume_path
    }), 200

@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    student, err, code = get_student_from_token()
    if err:
        return err, code

    data = request.get_json()
    student.full_name = data.get('full_name', student.full_name)
    student.branch = data.get('branch', student.branch)
    student.year = data.get('year', student.year)
    student.cgpa = data.get('cgpa', student.cgpa)
    student.skills = data.get('skills', student.skills)
    student.phone = data.get('phone', student.phone)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

# ─── APPLY FOR DRIVE ──────────────────────────────────────────────
@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
@jwt_required()
def apply_drive(drive_id):
    student, err, code = get_student_from_token()
    if err:
        return err, code

    drive = Drive.query.get_or_404(drive_id)

    # Check drive is approved
    if drive.status != 'approved':
        return jsonify({'message': 'This drive is not open for applications'}), 400

    # Check resume upload
    if not student.resume_path:
        return jsonify({'message': 'Please upload your resume PDF in the Profile tab before applying'}), 400

    # Check deadline
    if drive.application_deadline and datetime.utcnow() > drive.application_deadline:
        return jsonify({'message': 'Application deadline has passed'}), 400

    # Check eligibility - CGPA
    if drive.eligibility_cgpa:
        if student.cgpa is None:
            return jsonify({'message': 'Please update your CGPA in your profile before applying'}), 400
        if student.cgpa < drive.eligibility_cgpa:
            return jsonify({'message': f'Minimum CGPA required is {drive.eligibility_cgpa}'}), 400

    # Check eligibility - Branch
    if drive.eligibility_branch:
        if not student.branch:
            return jsonify({'message': 'Please update your Branch in your profile before applying'}), 400
        allowed_branches = [b.strip().upper() for b in drive.eligibility_branch.split(',')]
        if student.branch.upper() not in allowed_branches:
            return jsonify({'message': f'This drive is only for {drive.eligibility_branch} students'}), 400

    # Check eligibility - Year
    if drive.eligibility_year:
        if student.year is None:
            return jsonify({'message': 'Please update your Year in your profile before applying'}), 400
        if student.year != drive.eligibility_year:
            return jsonify({'message': f'This drive is only for year {drive.eligibility_year} students'}), 400

    # Check duplicate application
    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()
    if existing:
        return jsonify({'message': 'You have already applied for this drive'}), 400

    application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status='applied'
    )
    db.session.add(application)
    db.session.commit()
    

    # Clear student's dashboard cache so they see updated apply status
    from cache import delete_cache
    delete_cache(f'student_dashboard_{student.id}')

    return jsonify({'message': 'Application submitted successfully!'}), 201
    

# ─── VIEW MY APPLICATIONS ─────────────────────────────────────────
@student_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    student, err, code = get_student_from_token()
    if err:
        return err, code

    applications_data = db.session.query(
        Application, Drive, Company.company_name
    ).outerjoin(Drive, Application.drive_id == Drive.id)\
     .outerjoin(Company, Drive.company_id == Company.id)\
     .filter(Application.student_id == student.id).all()

    result = []
    for a, drive, company_name in applications_data:
        result.append({
            'application_id': a.id,
            'drive_id': a.drive_id,
            'drive_name': drive.drive_name if drive else '',
            'job_title': drive.job_title if drive else '',
            'company_name': company_name if company_name else '',
            'status': a.status,
            'application_date': a.application_date.isoformat(),
            'interview_date': a.interview_date.isoformat() if a.interview_date else None,
            'feedback': a.feedback
        })
    return jsonify(result), 200

# ─── SEARCH DRIVES ────────────────────────────────────────────────
@student_bp.route('/drives/search', methods=['GET'])
@jwt_required()
def search_drives():
    student, err, code = get_student_from_token()
    if err:
        return err, code

    search = request.args.get('search', '').strip()
    drives_data = db.session.query(Drive, Company.company_name).outerjoin(
        Company, Drive.company_id == Company.id
    ).filter(
        Drive.status == 'approved',
        Drive.job_title.ilike(f'%{search}%')
    ).all()

    result = []
    for d, company_name in drives_data:
        result.append({
            'id': d.id,
            'drive_name': d.drive_name,
            'job_title': d.job_title,
            'company_name': company_name or '',
            'location': d.location,
            'salary': d.salary,
            'eligibility_cgpa': d.eligibility_cgpa,
            'eligibility_branch': d.eligibility_branch
        })
    return jsonify(result), 200

# ─── GET COMPANIES (Student perspective) ───────────────────────────
@student_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    student, err, code = get_student_from_token()
    if err:
        return err, code

    companies = Company.query.filter_by(approval_status='approved', is_blacklisted=False).all()
    result = []
    for c in companies:
        result.append({
            'id': c.id,
            'company_name': c.company_name,
            'industry': c.industry,
            'location': c.location,
            'website': c.website,
            'hr_contact': c.hr_contact,
            'description': c.description
        })
    return jsonify(result), 200

# ─── GET COMPANY DETAILS (Student perspective) ────────────────────
@student_bp.route('/companies/<int:company_id>', methods=['GET'])
@jwt_required()
def get_company_details(company_id):
    student, err, code = get_student_from_token()
    if err:
        return err, code

    company = Company.query.filter_by(id=company_id, approval_status='approved', is_blacklisted=False).first_or_404()
    
    # Get active approved drives for this company
    drives = Drive.query.filter_by(company_id=company.id, status='approved').all()
    drive_list = []
    for d in drives:
        drive_list.append({
            'id': d.id,
            'drive_name': d.drive_name,
            'job_title': d.job_title,
            'salary': d.salary,
            'location': d.location,
            'application_deadline': d.application_deadline.isoformat() if d.application_deadline else None
        })

    return jsonify({
        'id': company.id,
        'company_name': company.company_name,
        'industry': company.industry,
        'location': company.location,
        'website': company.website,
        'hr_contact': company.hr_contact,
        'description': company.description,
        'drives': drive_list
    }), 200

# ─── GET DRIVE DETAILS (Student perspective) ──────────────────────
@student_bp.route('/drives/<int:drive_id>', methods=['GET'])
@jwt_required()
def get_drive_details(drive_id):
    student, err, code = get_student_from_token()
    if err:
        return err, code

    drive = Drive.query.get_or_404(drive_id)
    company = Company.query.get(drive.company_id)
    
    already_applied = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive.id
    ).first()

    return jsonify({
        'id': drive.id,
        'drive_name': drive.drive_name,
        'job_title': drive.job_title,
        'job_description': drive.job_description,
        'eligibility_branch': drive.eligibility_branch,
        'eligibility_cgpa': drive.eligibility_cgpa,
        'eligibility_year': drive.eligibility_year,
        'salary': drive.salary,
        'location': drive.location,
        'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
        'company_name': company.company_name if company else '',
        'company_id': company.id if company else None,
        'already_applied': bool(already_applied)
    }), 200

# ─── UPLOAD RESUME ────────────────────────────────────────────────
@student_bp.route('/upload-resume', methods=['POST'])
@jwt_required()
def upload_resume():
    from werkzeug.utils import secure_filename
    from flask import current_app
    import os

    student, err, code = get_student_from_token()
    if err:
        return err, code

    if 'resume' not in request.files:
        return jsonify({'message': 'No file uploaded'}), 400

    file = request.files['resume']

    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    # Only allow PDF files
    if not file.filename.endswith('.pdf'):
        return jsonify({'message': 'Only PDF files are allowed'}), 400

    filename = secure_filename(f"student_{student.id}_resume.pdf")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    student.resume_path = filename
    db.session.commit()

    return jsonify({'message': 'Resume uploaded successfully!', 'resume_path': filename}), 200


# ─── DOWNLOAD RESUME ──────────────────────────────────────────────
@student_bp.route('/resume/<int:student_id>', methods=['GET'])
@jwt_required()
def get_resume(student_id):
    from flask import send_from_directory, current_app
    import os

    claims = get_jwt()
    if claims.get('role') == 'student':
        user_id = int(get_jwt_identity())
        student_owner = Student.query.filter_by(user_id=user_id).first()
        if not student_owner or student_owner.id != student_id:
            return jsonify({'message': 'Access denied'}), 403

    student = Student.query.get_or_404(student_id)

    if not student.resume_path:
        return jsonify({'message': 'No resume uploaded'}), 404

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        student.resume_path,
        as_attachment=True
    )


# ─── EXPORT CSV (Async Job) ───────────────────────────────────────
@student_bp.route('/export-csv', methods=['POST'])
@jwt_required()
def export_csv():
    student, err, code = get_student_from_token()
    if err:
        return err, code

    from tasks import export_applications_csv
    export_applications_csv.delay(student.id)

    return jsonify({'message': 'Export started! You will receive an email shortly.'}), 200
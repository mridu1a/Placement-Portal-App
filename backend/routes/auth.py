from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Student, Company

auth_bp = Blueprint('auth', __name__)

# ─── REGISTER (Students & Companies only) ───────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate required fields
    if not data.get('username') or not data.get('email') or not data.get('password') or not data.get('role'):
        return jsonify({'message': 'All fields are required'}), 400

    if data['role'] == 'admin':
        return jsonify({'message': 'Admin registration not allowed'}), 403

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    # Create user
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        role=data['role']
    )
    db.session.add(new_user)
    db.session.flush()  # get new_user.id before commit

    # Create role-specific profile
    if data['role'] == 'student':
        student = Student(
            user_id=new_user.id,
            full_name=data.get('full_name', ''),
            branch=data.get('branch', ''),
            year=data.get('year', None),
            cgpa=data.get('cgpa', None),
            phone=data.get('phone', '')
        )
        db.session.add(student)

    elif data['role'] == 'company':
        company = Company(
            user_id=new_user.id,
            company_name=data.get('company_name', ''),
            industry=data.get('industry', ''),
            location=data.get('location', ''),
            website=data.get('website', ''),
            hr_contact=data.get('hr_contact', ''),
            description=data.get('description', '')
        )
        db.session.add(company)

    db.session.commit()
    return jsonify({'message': f'{data["role"].capitalize()} registered successfully!'}), 201


# ─── LOGIN (All roles) ───────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    if not user.is_active:
        return jsonify({'message': 'Your account has been deactivated'}), 403

    # Create JWT token
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'username': user.username,
            'role': user.role
        }
    )

    return jsonify({
        'access_token': access_token,
        'role': user.role,
        'username': user.username,
        'message': 'Login successful!'
    }), 200
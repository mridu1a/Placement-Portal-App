from flask import Flask, app
import os
from flask_cors import CORS
from flask_mail import Mail
from extensions import db, jwt
from celery_config import make_celery

mail = Mail()
celery = None

def create_app():
    
    app = Flask(__name__, instance_path=os.path.join(os.path.dirname(__file__), 'instance'))

    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, 'placement_portal.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'

    # Mail configuration (MailHog for local testing)
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 1025
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = None
    app.config['MAIL_PASSWORD'] = None
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@placementportal.com'

    # Celery configuration
    
    app.config['broker_url'] = 'redis://127.0.0.1:6379/0'
    app.config['result_backend'] = 'redis://127.0.0.1:6379/0'
    
    # Upload folder configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)

    # Initialize Celery
    global celery
    celery = make_celery(app)
    celery.conf.broker_url = 'redis://localhost:6379/0'
    celery.conf.result_backend = 'redis://localhost:6379/0'

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    return app

app = create_app()

# Auto-create database and admin on first run
with app.app_context():
    from extensions import db
    from models import User
    from werkzeug.security import generate_password_hash
    
    db.create_all()
    
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin_user = User(
            username='admin',
            email='admin@placement.com',
            password=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created automatically!")

if __name__ == '__main__':
    app.run(debug=True)


from app import app
from extensions import db
from models import User, Company, Student, Drive, Application
from werkzeug.security import generate_password_hash

def create_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ All tables created!")

        # Check if admin already exists
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
            print("✅ Admin user created!")
            print("   Username: admin")
            print("   Password: admin123")
        else:
            print("ℹ️  Admin already exists, skipping.")

if __name__ == '__main__':
    create_database()
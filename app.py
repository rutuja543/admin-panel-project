import os
from flask import Flask, render_template, redirect, url_for
from flask_login import login_required
from werkzeug.security import generate_password_hash
from extensions import db, login_manager
from models import Student, Course, AdminUser
from admin import init_admin
from auth import auth_bp


def create_app():
    app = Flask(__name__)

    # ─── Configuration ────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///admin_panel.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ─── Initialize extensions ────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)

    # ─── Register blueprints ──────────────────────────────────────────────────
    app.register_blueprint(auth_bp)

    # ─── Initialize Flask-Admin ───────────────────────────────────────────────
    init_admin(app)

    # ─── Dashboard route (protected) ─────────────────────────────────────────
    @app.route("/")
    @app.route("/dashboard")
    @login_required
    def dashboard():
        total_students = Student.query.count()
        total_courses = Course.query.count()
        active_students = Student.query.filter_by(status="Active").count()
        inactive_students = Student.query.filter_by(status="Inactive").count()
        recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
        return render_template(
            "dashboard.html",
            total_students=total_students,
            total_courses=total_courses,
            active_students=active_students,
            inactive_students=inactive_students,
            recent_students=recent_students,
        )

    # ─── Create tables and seed sample data on first run ─────────────────────
    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    """Insert sample data if the database is empty."""
    if AdminUser.query.count() == 0:
        admin = AdminUser(
            username="admin",
            password_hash=generate_password_hash("admin123"),
        )
        db.session.add(admin)
        db.session.commit()

    if Course.query.count() == 0:
        courses = [
            Course(course_name="Python Programming", duration="3 months", description="Learn Python from scratch to advanced level."),
            Course(course_name="Web Development", duration="4 months", description="Full-stack web development with HTML, CSS, JS, and Flask."),
            Course(course_name="Data Science", duration="6 months", description="Data analysis, visualization, and machine learning."),
            Course(course_name="Machine Learning", duration="5 months", description="Supervised, unsupervised, and deep learning techniques."),
        ]
        db.session.add_all(courses)

    if Student.query.count() == 0:
        from datetime import datetime, timedelta
        students = [
            Student(name="Alice Johnson", email="alice@example.com", course="Python Programming", status="Active", created_at=datetime.utcnow() - timedelta(days=10)),
            Student(name="Bob Smith", email="bob@example.com", course="Web Development", status="Active", created_at=datetime.utcnow() - timedelta(days=8)),
            Student(name="Carol White", email="carol@example.com", course="Data Science", status="Inactive", created_at=datetime.utcnow() - timedelta(days=5)),
            Student(name="David Brown", email="david@example.com", course="Machine Learning", status="Active", created_at=datetime.utcnow() - timedelta(days=3)),
            Student(name="Eva Martinez", email="eva@example.com", course="Python Programming", status="Active", created_at=datetime.utcnow() - timedelta(days=1)),
            Student(name="Frank Lee", email="frank@example.com", course="Web Development", status="Inactive", created_at=datetime.utcnow()),
        ]
        db.session.add_all(students)

    db.session.commit()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=False)

from extensions import db
from flask_login import UserMixin
from datetime import datetime


# ─── Student Model ────────────────────────────────────────────────────────────
class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    course = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Active")  # Active / Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Student {self.name}>"


# ─── Course Model ─────────────────────────────────────────────────────────────
class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False, unique=True)
    duration = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Course {self.course_name}>"


# ─── Admin User Model (for login) ─────────────────────────────────────────────
class AdminUser(db.Model, UserMixin):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<AdminUser {self.username}>"

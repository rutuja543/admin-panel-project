from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask_login import current_user
from wtforms import validators
from extensions import db
from models import Student, Course


# ─── Secure Base View — blocks access unless logged in ───────────────────────
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login"))


# ─── Custom Dashboard (index) view ────────────────────────────────────────────
class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        return redirect(url_for("dashboard"))

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login"))


# ─── Student Admin View ───────────────────────────────────────────────────────
class StudentView(SecureModelView):
    # Week 2: Column customization, search, filters, sorting, pagination
    column_list = ["id", "name", "email", "course", "status", "created_at"]
    column_searchable_list = ["name", "email"]
    column_filters = ["course", "status"]
    column_sortable_list = ["name", "email", "course", "status", "created_at"]
    column_default_sort = ("created_at", True)
    page_size = 10

    # Week 2: Friendly column labels
    column_labels = {
        "id": "ID",
        "name": "Full Name",
        "email": "Email Address",
        "course": "Course",
        "status": "Status",
        "created_at": "Enrolled On",
    }

    # Week 3: Form field configuration with validation
    form_columns = ["name", "email", "course", "status"]
    form_args = {
        "name": {
            "label": "Full Name",
            "validators": [validators.DataRequired(), validators.Length(min=2, max=100)],
        },
        "email": {
            "label": "Email Address",
            "validators": [
                validators.DataRequired(),
                validators.Email(message="Please enter a valid email address."),
            ],
        },
        "course": {
            "label": "Course",
            "validators": [validators.DataRequired()],
        },
        "status": {
            "label": "Status",
            "validators": [validators.DataRequired()],
        },
    }

    # Week 3: Restrict choices for status field
    form_choices = {
        "status": [("Active", "Active"), ("Inactive", "Inactive")],
    }

    # Week 3: Detail view columns
    column_details_list = ["id", "name", "email", "course", "status", "created_at"]
    can_view_details = True

    # Week 4: Bulk actions
    @action("mark_active", "Mark as Active", "Mark selected students as Active?")
    def action_mark_active(self, ids):
        students = Student.query.filter(Student.id.in_(ids)).all()
        for s in students:
            s.status = "Active"
        db.session.commit()

    @action("mark_inactive", "Mark as Inactive", "Mark selected students as Inactive?")
    def action_mark_inactive(self, ids):
        students = Student.query.filter(Student.id.in_(ids)).all()
        for s in students:
            s.status = "Inactive"
        db.session.commit()

    # Week 5: Column formatting — color-coded status badge
    def _status_formatter(view, context, model, name):
        badge = "success" if model.status == "Active" else "secondary"
        return f'<span class="badge bg-{badge}">{model.status}</span>'

    column_formatters = {"status": _status_formatter}


# ─── Course Admin View ────────────────────────────────────────────────────────
class CourseView(SecureModelView):
    column_list = ["id", "course_name", "duration", "description"]
    column_searchable_list = ["course_name"]
    column_sortable_list = ["course_name", "duration"]
    page_size = 10

    column_labels = {
        "id": "ID",
        "course_name": "Course Name",
        "duration": "Duration",
        "description": "Description",
    }

    form_columns = ["course_name", "duration", "description"]
    form_args = {
        "course_name": {
            "label": "Course Name",
            "validators": [validators.DataRequired(), validators.Length(min=2, max=100)],
        },
        "duration": {
            "label": "Duration (e.g. 3 months)",
            "validators": [validators.DataRequired()],
        },
        "description": {
            "label": "Description",
        },
    }

    can_view_details = True
    column_details_list = ["id", "course_name", "duration", "description"]


# ─── Initialize Flask-Admin ───────────────────────────────────────────────────
def init_admin(app):
    admin = Admin(
        app,
        name="Admin Panel",
        index_view=MyAdminIndexView(),
    )
    admin.add_view(StudentView(Student, db.session, name="Students", menu_icon_type="fa", menu_icon_value="fa-user-graduate"))
    admin.add_view(CourseView(Course, db.session, name="Courses", menu_icon_type="fa", menu_icon_value="fa-book"))
    return admin

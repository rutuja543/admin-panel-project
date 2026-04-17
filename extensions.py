from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Shared extension instances — imported by app.py, models.py, admin.py, auth.py
db = SQLAlchemy()
login_manager = LoginManager()

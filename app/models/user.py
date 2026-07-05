from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """User account database model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships (will add in later phases as models are created)
    # resumes = db.relationship('Resume', backref='owner', lazy=True)
    # readiness = db.relationship('PlacementReadiness', backref='user', uselist=False, lazy=True)

    def set_password(self, password):
        """Generates a secure hash for the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies if the provided password matches the secure hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"

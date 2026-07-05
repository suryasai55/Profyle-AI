from datetime import datetime, timezone
from app import db

class Resume(db.Model):
    """Resume database model for NLP parse results and S3 references."""
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(512), nullable=True)  # Will hold S3 object key in production
    score = db.Column(db.Float, default=0.0)
    detected_skills = db.Column(db.Text, default='')   # Comma-separated or JSON list of skills
    missing_skills = db.Column(db.Text, default='')    # Comma-separated or JSON list of missing skills
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship back to User
    user = db.relationship('User', backref=db.backref('resumes', cascade='all, delete-orphan', lazy=True))

    def __repr__(self):
        return f"<Resume {self.filename} Score={self.score}>"

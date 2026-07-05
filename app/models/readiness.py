from datetime import datetime, timezone
from app import db

class PlacementReadiness(db.Model):
    """Model tracking user aggregate readiness ratings and dashboard progress."""
    __tablename__ = 'placement_readiness'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    resume_score = db.Column(db.Float, default=0.0)
    aptitude_score = db.Column(db.Float, default=0.0)
    interview_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    readiness_status = db.Column(db.String(50), default='Needs Improvement')  # Ready | Almost Ready | Needs Improvement
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship back to User
    user = db.relationship('User', backref=db.backref('readiness', uselist=False, cascade='all, delete-orphan', lazy=True))

    def calculate_overall(self):
        """Calculates weighted readiness rating: 40% Resume, 30% Aptitude, 30% Interview."""
        res_score = self.resume_score if self.resume_score is not None else 0.0
        apt_score = self.aptitude_score if self.aptitude_score is not None else 0.0
        int_score = self.interview_score if self.interview_score is not None else 0.0
        self.overall_score = (res_score * 0.40) + (apt_score * 0.30) + (int_score * 0.30)
        
        if self.overall_score >= 80:
            self.readiness_status = 'Ready'
        elif self.overall_score >= 50:
            self.readiness_status = 'Almost Ready'
        else:
            self.readiness_status = 'Needs Improvement'

    def __repr__(self):
        return f"<PlacementReadiness User={self.user_id} Score={self.overall_score} Status={self.readiness_status}>"

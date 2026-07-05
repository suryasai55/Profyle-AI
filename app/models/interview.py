from datetime import datetime, timezone
from app import db

class Question(db.Model):
    """Database model for interview questions."""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False, index=True)  # Python | SQL | AWS | Docker | Git | HR | Behavioral
    difficulty = db.Column(db.String(50), nullable=False)             # Easy | Medium | Hard
    question_text = db.Column(db.Text, nullable=False)
    answer_reveal = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Question Cat={self.category} Diff={self.difficulty}>"

class Bookmark(db.Model):
    """Database model for user-bookmarked interview questions."""
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('bookmarks', cascade='all, delete-orphan', lazy=True))
    question = db.relationship('Question', backref=db.backref('bookmarked_by', cascade='all, delete-orphan', lazy=True))

    __table_args__ = (db.UniqueConstraint('user_id', 'question_id', name='_user_question_bookmark_uc'),)

    def __repr__(self):
        return f"<Bookmark User={self.user_id} Question={self.question_id}>"

class InterviewHistory(db.Model):
    """Database model for storing history of user's answers and completed questions."""
    __tablename__ = 'interview_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    user_answer = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref=db.backref('interview_history', cascade='all, delete-orphan', lazy=True))
    question = db.relationship('Question', backref=db.backref('history_records', cascade='all, delete-orphan', lazy=True))

    __table_args__ = (db.UniqueConstraint('user_id', 'question_id', name='_user_question_history_uc'),)

    def __repr__(self):
        return f"<InterviewHistory User={self.user_id} Question={self.question_id} Completed={self.is_completed}>"

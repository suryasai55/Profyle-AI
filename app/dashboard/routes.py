from flask import render_template
from flask_login import current_user
from app.dashboard import dashboard
from app.models.resume import Resume
from app.models.readiness import PlacementReadiness
from app.models.interview import Question, Bookmark, InterviewHistory

@dashboard.route('/')
def index():
    """Render the dashboard home page with user-specific metrics if authenticated."""
    metrics = {
        'has_resume': False,
        'resume_filename': None,
        'resume_score': 0,
        'detected_skills_count': 0,
        'missing_skills_count': 0,
        'readiness_score': 0,
        'readiness_status': 'Needs Improvement',
        'readiness_resume': 0,
        'readiness_aptitude': 0,
        'readiness_interview': 0,
        'completed_questions': 0,
        'bookmarked_questions': 0,
        'total_questions': 0,
        'recent_resumes': []
    }
    
    # Query database stats if user is authenticated
    if current_user.is_authenticated:
        # 1. Fetch latest resume
        latest_resume = Resume.query.filter_by(user_id=current_user.id)\
                                    .order_by(Resume.uploaded_at.desc()).first()
        if latest_resume:
            metrics['has_resume'] = True
            metrics['resume_filename'] = latest_resume.filename
            metrics['resume_score'] = int(latest_resume.score)
            
            # Count skills
            detected_list = [s for s in latest_resume.detected_skills.split(',') if s.strip()] if latest_resume.detected_skills else []
            missing_list = [s for s in latest_resume.missing_skills.split(',') if s.strip()] if latest_resume.missing_skills else []
            metrics['detected_skills_count'] = len(detected_list)
            metrics['missing_skills_count'] = len(missing_list)
            
        # 2. Fetch placement readiness
        readiness = PlacementReadiness.query.filter_by(user_id=current_user.id).first()
        if readiness:
            metrics['readiness_score'] = int(readiness.overall_score)
            metrics['readiness_status'] = readiness.readiness_status
            metrics['readiness_resume'] = int(readiness.resume_score)
            metrics['readiness_aptitude'] = int(readiness.aptitude_score)
            metrics['readiness_interview'] = int(readiness.interview_score)
            
        # 3. Fetch interview stats
        metrics['completed_questions'] = InterviewHistory.query.filter_by(user_id=current_user.id, is_completed=True).count()
        metrics['bookmarked_questions'] = Bookmark.query.filter_by(user_id=current_user.id).count()
        
        # 4. Fetch recent resumes list
        metrics['recent_resumes'] = Resume.query.filter_by(user_id=current_user.id)\
                                                .order_by(Resume.uploaded_at.desc()).limit(5).all()

    # Always count total questions in DB for progress bars
    metrics['total_questions'] = Question.query.count() or 50  # default fallback if DB not preloaded yet
    
    return render_template('dashboard/index.html', metrics=metrics)

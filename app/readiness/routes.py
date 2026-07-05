from flask import render_template
from flask_login import login_required, current_user
from app import db
from app.readiness import readiness
from app.models.readiness import PlacementReadiness

@readiness.route('/score', methods=['GET'])
@login_required
def score():
    """Evaluate and display candidate aggregate readiness score and recommendations."""
    # 1. Fetch user's readiness record
    user_readiness = PlacementReadiness.query.filter_by(user_id=current_user.id).first()
    
    # 2. Auto-initialize record with defaults if it doesn't exist
    if not user_readiness:
        try:
            user_readiness = PlacementReadiness(
                user_id=current_user.id,
                resume_score=0.0,
                aptitude_score=0.0,
                interview_score=0.0,
                overall_score=0.0,
                readiness_status='Needs Improvement'
            )
            db.session.add(user_readiness)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            from flask import current_app
            current_app.logger.error(f"Readiness Init Error: {str(e)}")
            
    # 3. Compile custom suggestions based on scores
    suggestions = []
    
    # Resume score suggestions
    res_score = user_readiness.resume_score
    if res_score < 50:
        suggestions.append({
            'category': 'Resume',
            'icon': 'fa-file-pdf',
            'type': 'danger',
            'text': 'Your resume score is low. Upload a PDF resume containing relevant keywords in Python, SQL, Git, and Docker to improve your baseline.'
        })
    elif res_score < 80:
        suggestions.append({
            'category': 'Resume',
            'icon': 'fa-file-pdf',
            'type': 'warning',
            'text': 'Your resume has moderate alignment. Check the Skill Gap Detector to see which specific libraries you can add to boost your match rating.'
        })
    else:
        suggestions.append({
            'category': 'Resume',
            'icon': 'fa-file-pdf',
            'type': 'success',
            'text': 'Great job! Your resume matches industry skillsets exceptionally well.'
        })
        
    # Aptitude score suggestions
    apt_score = user_readiness.aptitude_score
    if apt_score < 50:
        suggestions.append({
            'category': 'Aptitude',
            'icon': 'fa-brain',
            'type': 'danger',
            'text': 'Aptitude performance is key for screening rounds. Practice logical reasoning and quantitative math sheets to elevate this score.'
        })
    else:
        suggestions.append({
            'category': 'Aptitude',
            'icon': 'fa-brain',
            'type': 'success',
            'text': 'Your aptitude baseline meets top screening thresholds.'
        })
        
    # Interview prep suggestions
    int_score = user_readiness.interview_score
    if int_score < 50:
        suggestions.append({
            'category': 'Technical Q&A',
            'icon': 'fa-comments',
            'type': 'danger',
            'text': 'Complete mock Q&A preparation rounds in our Interview Prep portal. Bookmarking and answering questions will directly raise this score.'
        })
    else:
        suggestions.append({
            'category': 'Technical Q&A',
            'icon': 'fa-comments',
            'type': 'success',
            'text': 'Excellent job! You are well-prepared to face technical panels.'
        })
        
    return render_template(
        'readiness/score.html',
        readiness=user_readiness,
        suggestions=suggestions
    )

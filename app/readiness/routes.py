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

@readiness.route('/jobs', methods=['GET'])
@login_required
def jobs():
    """Render job matches based on the candidate's skills alignment."""
    from app.models.resume import Resume
    latest_resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).first()
    
    # Determine detected skills
    detected_skills = []
    if latest_resume and latest_resume.detected_skills:
        detected_skills = [s.strip().lower() for s in latest_resume.detected_skills.split(',') if s.strip()]
        
    # Compile list of jobs
    jobs_list = [
        {
            "id": 1,
            "title": "Junior Python Developer",
            "company": "TechCorp Solutions",
            "location": "San Francisco, CA (Hybrid)",
            "role": "Python Developer",
            "required_skills": ["python", "sql", "git", "flask"],
            "salary": "$85,000 - $105,000"
        },
        {
            "id": 2,
            "title": "Data Analyst (Analytics Team)",
            "company": "DataFlo Inc.",
            "location": "New York, NY (Remote)",
            "role": "Data Analyst",
            "required_skills": ["sql", "python", "data science"],
            "salary": "$90,000 - $110,000"
        },
        {
            "id": 3,
            "title": "Machine Learning Engineer",
            "company": "NeuraLink Systems",
            "location": "Boston, MA (On-site)",
            "role": "ML Engineer",
            "required_skills": ["python", "machine learning", "data science", "nlp"],
            "salary": "$120,000 - $145,000"
        },
        {
            "id": 4,
            "title": "Junior DevOps Engineer",
            "company": "CloudOps & Co.",
            "location": "Austin, TX (Remote)",
            "role": "DevOps Engineer",
            "required_skills": ["docker", "jenkins", "git", "aws", "python"],
            "salary": "$95,000 - $115,000"
        },
        {
            "id": 5,
            "title": "Backend Systems Developer",
            "company": "AppForge Studio",
            "location": "Seattle, WA (Hybrid)",
            "role": "Backend Developer",
            "required_skills": ["python", "sql", "flask", "docker", "aws"],
            "salary": "$110,000 - $130,000"
        }
    ]
    
    # Calculate match score dynamically
    for job in jobs_list:
        matched_skills = [s for s in job["required_skills"] if s in detected_skills]
        match_ratio = (len(matched_skills) / len(job["required_skills"])) * 100 if job["required_skills"] else 100
        # Add basic base score if they have any python skills
        if match_ratio == 0:
            if "python" in detected_skills:
                match_ratio = 45
            elif "sql" in detected_skills:
                match_ratio = 30
            else:
                match_ratio = 15
        job["match_score"] = min(100, int(match_ratio))
        job["matched_skills"] = [s.capitalize() for s in matched_skills]
        job["missing_skills"] = [s.capitalize() for s in job["required_skills"] if s not in detected_skills]
        
    # Sort jobs by match score descending
    jobs_list.sort(key=lambda x: x["match_score"], reverse=True)
    
    return render_template('readiness/jobs.html', jobs=jobs_list)

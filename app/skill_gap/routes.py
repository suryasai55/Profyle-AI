import os
import json
from flask import render_template, request, current_app
from flask_login import login_required, current_user
from app.skill_gap import skill_gap
from app.models.resume import Resume

def load_skills_data():
    """Loads the skill roles and course recommendations database from JSON."""
    json_path = os.path.join(current_app.root_path, '../datasets/skill_roles.json')
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        current_app.logger.error(f"Error loading skill roles dataset: {str(e)}")
        return {"roles": {}, "course_recommendations": {}}

@skill_gap.route('/analysis', methods=['GET'])
@login_required
def analysis():
    """Compare user's parsed skills against target role requirements and provide learning paths."""
    skills_db = load_skills_data()
    roles = skills_db.get('roles', {})
    courses_db = skills_db.get('course_recommendations', {})
    
    # 1. Fetch user's latest resume
    latest_resume = Resume.query.filter_by(user_id=current_user.id)\
                                .order_by(Resume.uploaded_at.desc()).first()
                                
    # Determine user's parsed skills set
    user_skills = set()
    if latest_resume and latest_resume.detected_skills:
        user_skills = {s.strip() for s in latest_resume.detected_skills.split(',') if s.strip()}
        
    # 2. Get active role (defaults to Python Developer)
    role_keys = list(roles.keys())
    selected_role_id = request.args.get('role')
    
    if not selected_role_id or selected_role_id not in roles:
        selected_role_id = role_keys[0] if role_keys else None
        
    selected_role = roles.get(selected_role_id) if selected_role_id else None
    
    # 3. Analyze gaps
    matched_skills = []
    missing_skills = []
    matching_percentage = 0
    missing_courses = []
    
    if selected_role:
        required_skills = selected_role.get('required_skills', [])
        for skill in required_skills:
            if skill in user_skills:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
                # Fetch course recommendation
                if skill in courses_db:
                    missing_courses.append({
                        'skill': skill,
                        'title': courses_db[skill]['title'],
                        'platform': courses_db[skill]['platform'],
                        'priority': courses_db[skill]['priority'],
                        'link': courses_db[skill]['link']
                    })
                    
        # Sort courses by priority (High first)
        missing_courses.sort(key=lambda x: x['priority'] == 'High', reverse=True)
        
        if required_skills:
            matching_percentage = int((len(matched_skills) / len(required_skills)) * 100)
            
    return render_template(
        'skill_gap/analysis.html',
        roles=roles,
        selected_role_id=selected_role_id,
        selected_role=selected_role,
        has_resume=latest_resume is not None,
        matching_percentage=matching_percentage,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        courses=missing_courses
    )

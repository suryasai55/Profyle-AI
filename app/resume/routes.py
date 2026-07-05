import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.resume import resume
from app.models.resume import Resume
from app.models.readiness import PlacementReadiness
from app.resume.parser import parse_resume
from app.utils.s3 import upload_file_to_s3

def allowed_file(filename):
    """Checks if the uploaded file has a PDF extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@resume.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Handles PDF resume upload, executes NLP skill parsing, and logs details."""
    if request.method == 'POST':
        # 1. Validation check for file in request
        if 'resume' not in request.files:
            flash('No file section in the upload request.', 'danger')
            return redirect(request.url)
            
        file = request.files['resume']
        
        # 2. Check if file is empty
        if file.filename == '':
            flash('No resume file selected.', 'danger')
            return redirect(request.url)
            
        # 3. Verify extension
        if file and allowed_file(file.filename):
            base_name = secure_filename(file.filename)
            unique_filename = f"user_{current_user.id}_{base_name}"
            local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                # 4. Save file locally first to execute NLP analysis
                file.save(local_path)
                
                # 5. Execute NLTK and PyPDF2 Parser
                score, detected_skills, missing_skills = parse_resume(
                    local_path, 
                    current_app.config['NLTK_DATA_DIR']
                )
                
                # 6. Coordinate Storage (Production S3 vs. Dev Local)
                s3_key = None
                if current_app.config['USE_S3']:
                    with open(local_path, 'rb') as f:
                        s3_key, _ = upload_file_to_s3(f, unique_filename, current_app.config)
                    # If successfully saved to S3, purge local temp file
                    if s3_key:
                        try:
                            os.remove(local_path)
                        except Exception as rem_err:
                            current_app.logger.warning(f"Could not delete local temp file after S3 upload: {rem_err}")
                else:
                    # If local mode, we keep the local file saved in the local path
                    pass
                
                # 7. Write to Resume Database
                new_resume = Resume(
                    user_id=current_user.id,
                    filename=base_name,
                    s3_key=s3_key,
                    score=score,
                    detected_skills=','.join(detected_skills),
                    missing_skills=','.join(missing_skills)
                )
                db.session.add(new_resume)
                
                # 8. Update User's Placement Readiness Score
                readiness = PlacementReadiness.query.filter_by(user_id=current_user.id).first()
                if not readiness:
                    readiness = PlacementReadiness(user_id=current_user.id, resume_score=score)
                    db.session.add(readiness)
                else:
                    readiness.resume_score = score
                    
                readiness.calculate_overall()
                db.session.commit()
                
                flash(f"Resume '{base_name}' analyzed successfully!", 'success')
                return redirect(url_for('resume.results', resume_id=new_resume.id))
                
            except Exception as e:
                db.session.rollback()
                # Ensure local temp file is removed if an exception occurs during parse
                if os.path.exists(local_path) and current_app.config['USE_S3']:
                    try:
                        os.remove(local_path)
                    except:
                        pass
                current_app.logger.error(f"Resume Analysis Error: {str(e)}")
                flash(f"Analysis failed: {str(e)}", 'danger')
                return redirect(request.url)
        else:
            flash('Invalid file type. Only PDF files are allowed.', 'danger')
            return redirect(request.url)

    recent_resumes = []
    if current_user.is_authenticated:
        recent_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).limit(5).all()

    return render_template('resume/upload.html', recent_resumes=recent_resumes)

@resume.route('/results/<int:resume_id>')
@login_required
def results(resume_id):
    """Display the detailed NLP analysis results and skill mapping."""
    res = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    detected_skills = [s.strip() for s in res.detected_skills.split(',') if s.strip()]
    missing_skills = [s.strip() for s in res.missing_skills.split(',') if s.strip()]
    
    return render_template(
        'resume/results.html', 
        resume=res, 
        detected_skills=detected_skills, 
        missing_skills=missing_skills
    )

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.interview import interview
from app.models.interview import Question, Bookmark, InterviewHistory
from app.models.readiness import PlacementReadiness

@interview.route('/prep', methods=['GET'])
@login_required
def prep():
    """Display the Q&A preparation module, filtering by categories and search queries."""
    # 1. Fetch search and filter parameters
    selected_category = request.args.get('category', 'Python').strip()
    search_query = request.args.get('search', '').strip()
    
    # 2. Get list of distinct categories for sidebar statistics
    categories = ['Python', 'SQL', 'AWS', 'Docker', 'Git', 'HR', 'Behavioral']
    categories_stats = {}
    for cat in categories:
        total = Question.query.filter_by(category=cat).count()
        done = InterviewHistory.query.join(Question).filter(
            InterviewHistory.user_id == current_user.id,
            Question.category == cat,
            InterviewHistory.is_completed == True
        ).count()
        categories_stats[cat] = {'total': total, 'done': done}
        
    # 3. Query questions matching criteria
    query = Question.query
    if search_query:
        # If searching, look across all text, ignoring category filter initially or applying it
        # Let's search within all categories if they type something, or restrict it.
        # We will search within all questions to make discovery easier, or narrow by category.
        # Let's search globally to be user-friendly, or narrow by category if selected.
        query = query.filter(Question.question_text.contains(search_query) | Question.category.contains(search_query))
    else:
        query = query.filter_by(category=selected_category)
        
    questions_list = query.all()
    
    # 4. Fetch user's bookmarks and completed question IDs
    bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()
    bookmarked_ids = {b.question_id for b in bookmarks}
    
    completed_records = InterviewHistory.query.filter_by(user_id=current_user.id, is_completed=True).all()
    completed_ids = {c.question_id for c in completed_records}
    
    return render_template(
        'interview/prep.html',
        categories=categories,
        categories_stats=categories_stats,
        selected_category=selected_category,
        search_query=search_query,
        questions=questions_list,
        bookmarked_ids=bookmarked_ids,
        completed_ids=completed_ids
    )

@interview.route('/bookmark/toggle/<int:question_id>', methods=['GET'])
@login_required
def toggle_bookmark(question_id):
    """Toggle the bookmark state of a question for the active user."""
    # Ensure question exists
    question = Question.query.get_or_404(question_id)
    
    existing_bookmark = Bookmark.query.filter_by(
        user_id=current_user.id, 
        question_id=question_id
    ).first()
    
    category = request.args.get('category', 'Python')
    search = request.args.get('search', '')
    
    try:
        if existing_bookmark:
            db.session.delete(existing_bookmark)
            flash('Bookmark removed.', 'info')
        else:
            new_bookmark = Bookmark(user_id=current_user.id, question_id=question_id)
            db.session.add(new_bookmark)
            flash('Question bookmarked!', 'success')
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while toggling bookmark.', 'danger')
        
    return redirect(url_for('interview.prep', category=category, search=search))

@interview.route('/complete/toggle/<int:question_id>', methods=['GET'])
@login_required
def toggle_complete(question_id):
    """Toggle the completion state of a question and update user readiness scores."""
    question = Question.query.get_or_404(question_id)
    
    history = InterviewHistory.query.filter_by(
        user_id=current_user.id, 
        question_id=question_id
    ).first()
    
    category = request.args.get('category', 'Python')
    search = request.args.get('search', '')
    
    try:
        if history:
            history.is_completed = not history.is_completed
            msg = 'Question marked as incomplete.' if not history.is_completed else 'Question completed!'
        else:
            history = InterviewHistory(user_id=current_user.id, question_id=question_id, is_completed=True)
            db.session.add(history)
            msg = 'Question completed!'
            
        db.session.commit()
        flash(msg, 'success')
        
        # Recalculate Interview Score and Placement Readiness
        update_readiness_interview_score(current_user.id)
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating completion status.', 'danger')
        
    return redirect(url_for('interview.prep', category=category, search=search))

def update_readiness_interview_score(user_id):
    """Calculate aggregate interview score: 10 points per completed question (max 100)."""
    completed_count = InterviewHistory.query.filter_by(
        user_id=user_id, 
        is_completed=True
    ).count()
    
    # 10 completed questions = 100% interview score
    new_interview_score = min(completed_count * 10, 100)
    
    readiness = PlacementReadiness.query.filter_by(user_id=user_id).first()
    if not readiness:
        readiness = PlacementReadiness(user_id=user_id, interview_score=new_interview_score)
        db.session.add(readiness)
    else:
        readiness.interview_score = new_interview_score
        
    readiness.calculate_overall()
    db.session.commit()

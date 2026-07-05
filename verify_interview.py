import sys
from app import create_app, db
from app.models.user import User
from app.models.interview import Question, Bookmark, InterviewHistory
from app.models.readiness import PlacementReadiness

def verify_interview():
    print("Initializing test app context...")
    app = create_app('development')
    
    with app.app_context():
        # Verify questions table has data
        q_count = Question.query.count()
        print(f"Questions table count: {q_count}")
        if q_count == 0:
            print("FAIL: Preloaded questions table is empty.", file=sys.stderr)
            sys.exit(1)
            
        user = User.query.filter_by(email="test@example.com").first()
        if not user:
            print("Creating test user...")
            user = User(name="Test User", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
        user_id = user.id
        
        # Clean history
        Bookmark.query.filter_by(user_id=user_id).delete()
        InterviewHistory.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        first_q = Question.query.first()
        first_q_id = first_q.id

    with app.test_client() as client:
        print("Logging in...")
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # 1. Test GET prep page
        print("Requesting interview prep page...")
        prep_resp = client.get('/interview/prep?category=Python')
        if prep_resp.status_code != 200:
            print(f"FAIL: Prep page status code {prep_resp.status_code}", file=sys.stderr)
            sys.exit(1)
            
        # 2. Test Toggle Bookmark
        print(f"Toggling bookmark for Question ID {first_q_id}...")
        bookmark_resp = client.get(f'/interview/bookmark/toggle/{first_q_id}?category=Python', follow_redirects=True)
        if b"Question bookmarked!" not in bookmark_resp.data:
            print("FAIL: Bookmark message not in response.", file=sys.stderr)
            sys.exit(1)
            
        # Verify in DB
        with app.app_context():
            bm = Bookmark.query.filter_by(user_id=user_id, question_id=first_q_id).first()
            if not bm:
                print("FAIL: Bookmark record not found in database.", file=sys.stderr)
                sys.exit(1)
            print("SUCCESS: Bookmark toggled and logged successfully.")
            
        # 3. Test Toggle Complete
        print(f"Toggling completion for Question ID {first_q_id}...")
        complete_resp = client.get(f'/interview/complete/toggle/{first_q_id}?category=Python', follow_redirects=True)
        if b"Question completed!" not in complete_resp.data:
            print("FAIL: Completion message not in response.", file=sys.stderr)
            sys.exit(1)
            
        # Verify in DB and score calculation
        with app.app_context():
            hist = InterviewHistory.query.filter_by(user_id=user_id, question_id=first_q_id, is_completed=True).first()
            if not hist:
                print("FAIL: Interview history record not logged in database.", file=sys.stderr)
                sys.exit(1)
                
            readiness = PlacementReadiness.query.filter_by(user_id=user_id).first()
            if not readiness or readiness.interview_score != 10.0:
                print(f"FAIL: Interview score was not updated correctly. Score is {readiness.interview_score if readiness else None}", file=sys.stderr)
                sys.exit(1)
                
            print(f"Readiness Interview Score: {readiness.interview_score}")
            print(f"Readiness Overall Score: {readiness.overall_score}")
            print("SUCCESS: Completion toggled and placement readiness score recalculated successfully.")
            
        print("--- INTERVIEW PREPARATION MODULE FULLY FUNCTIONAL ---")
        sys.exit(0)

if __name__ == '__main__':
    verify_interview()

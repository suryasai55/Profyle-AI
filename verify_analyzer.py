import io
import os
import sys
from app import create_app, db
from app.models.user import User
from app.models.resume import Resume
from app.models.readiness import PlacementReadiness

# Minimal valid PDF content with Helvetica font text
MINIMAL_PDF_WITH_TEXT = (
    b"%PDF-1.4\n"
    b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
    b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
    b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj\n"
    b"4 0 obj <</Length 70>> stream\n"
    b"BT /F1 12 Tf 70 700 Td (Python SQL AWS Docker Git React Flask NLP Data Science) Tj ET\n"
    b"endstream\n"
    b"endobj\n"
    b"5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
    b"xref\n"
    b"0 6\n"
    b"0000000000 65535 f\n"
    b"0000000009 00000 n\n"
    b"0000000056 00000 n\n"
    b"0000000111 00000 n\n"
    b"0000000224 00000 n\n"
    b"0000000344 00000 n\n"
    b"trailer <</Size 6 /Root 1 0 R>>\n"
    b"startxref\n"
    b"421\n"
    b"%%EOF\n"
)

def verify_analyzer():
    print("Initializing test app context...")
    app = create_app('development')
    
    with app.app_context():
        # Ensure we have our test user
        user = User.query.filter_by(email="test@example.com").first()
        if not user:
            print("Creating test user...")
            user = User(name="Test User", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
        user_id = user.id

        # Clean old records
        Resume.query.filter_by(user_id=user_id).delete()
        PlacementReadiness.query.filter_by(user_id=user_id).delete()
        db.session.commit()

    with app.test_client() as client:
        print("Logging in...")
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })

        # Send post request with our custom PDF content
        print("Uploading test skills PDF resume...")
        response = client.post('/resume/upload', data={
            'resume': (io.BytesIO(MINIMAL_PDF_WITH_TEXT), 'test_analyzer_skills.pdf')
        }, follow_redirects=True)

        if b"analyzed successfully!" not in response.data:
            print("FAIL: Upload and analysis response did not contain success message.", file=sys.stderr)
            sys.exit(1)
        print("SUCCESS: Upload and analysis request succeeded.")

        # Verify database resume record
        with app.app_context():
            res = Resume.query.filter_by(user_id=user_id).first()
            if not res:
                print("FAIL: Resume record was not logged in DB.", file=sys.stderr)
                sys.exit(1)
                
            detected = res.detected_skills.split(',')
            missing = res.missing_skills.split(',')
            
            print(f"Detected skills in DB: {detected}")
            print(f"Missing skills in DB: {missing}")
            print(f"Calculated Score: {res.score}")
            
            # Assert core skills we wrote are in detected
            expected_detected = ['Python', 'SQL', 'AWS', 'Docker', 'Git', 'React', 'Flask', 'NLP', 'Data Science']
            for skill in expected_detected:
                if skill not in detected:
                    print(f"FAIL: Skill '{skill}' was not detected by NLP parser.", file=sys.stderr)
                    sys.exit(1)
            print("SUCCESS: All expected skills were parsed and detected successfully.")
            
            # Verify readiness score
            readiness = PlacementReadiness.query.filter_by(user_id=user_id).first()
            if not readiness:
                print("FAIL: PlacementReadiness record was not updated/created.", file=sys.stderr)
                sys.exit(1)
                
            print(f"Placement Readiness - Resume Score: {readiness.resume_score}")
            print(f"Placement Readiness - Overall Score: {readiness.overall_score}")
            print(f"Placement Readiness - Status: {readiness.readiness_status}")
            
            if readiness.resume_score != res.score:
                print(f"FAIL: Readiness resume score ({readiness.resume_score}) != Resume score ({res.score})", file=sys.stderr)
                sys.exit(1)
            print("SUCCESS: PlacementReadiness calculations updated correctly.")
            
        print("--- RESUME ANALYZER MODULE FULLY FUNCTIONAL ---")
        sys.exit(0)

if __name__ == '__main__':
    verify_analyzer()

import io
import os
import sys
from app import create_app, db
from app.models.user import User
from app.models.resume import Resume

def verify_upload():
    print("Initializing test app context...")
    app = create_app('development')
    
    # 1. Create a test user or retrieve existing
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        if not user:
            print("Creating test user...")
            user = User(name="Test User", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
        user_id = user.id

        # Clean old resumes to keep tests isolated
        Resume.query.filter_by(user_id=user_id).delete()
        db.session.commit()

    with app.test_client() as client:
        # Log in
        print("Logging in...")
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })

        # 2. Simulate Upload POST
        print("Sending upload POST with PDF file...")
        pdf_data = b"%PDF-1.4 mock pdf data header and body contents"
        upload_response = client.post('/resume/upload', data={
            'resume': (io.BytesIO(pdf_data), 'test_resume.pdf')
        }, follow_redirects=True)

        if b"uploaded successfully!" not in upload_response.data:
            print("FAIL: Upload response does not contain success flash message.", file=sys.stderr)
            sys.exit(1)
        print("SUCCESS: Upload request returned success flash message.")

        # 3. Verify file saved to local filesystem
        expected_filename = f"user_{user_id}_test_resume.pdf"
        expected_path = os.path.join(app.config['UPLOAD_FOLDER'], expected_filename)
        
        if not os.path.exists(expected_path):
            print(f"FAIL: File was not saved to {expected_path}", file=sys.stderr)
            sys.exit(1)
        print(f"SUCCESS: File successfully written to local development uploads directory: {expected_path}")

        # Clean up local file copy to keep system clean
        try:
            os.remove(expected_path)
            print("Cleaned up mock local file.")
        except Exception as e:
            print(f"Warning: Could not clean up file {expected_path}: {e}")

        # 4. Verify database record
        with app.app_context():
            res_rec = Resume.query.filter_by(user_id=user_id).first()
            if not res_rec:
                print("FAIL: Resume record was not found in database.", file=sys.stderr)
                sys.exit(1)
            if res_rec.filename != "test_resume.pdf":
                print(f"FAIL: Filename stored is '{res_rec.filename}', expected 'test_resume.pdf'", file=sys.stderr)
                sys.exit(1)
            print(f"SUCCESS: Resume db record verified successfully (Owner ID={res_rec.user_id}, Filename={res_rec.filename}).")
            
        print("--- RESUME UPLOAD MODULE FULLY FUNCTIONAL ---")
        sys.exit(0)

if __name__ == '__main__':
    verify_upload()

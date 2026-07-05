import sys
from app import create_app, db
from app.models.user import User

def verify_auth():
    print("Initializing test app context...")
    app = create_app('development')
    
    # 1. Clear database test entry to keep test idempotent
    with app.app_context():
        existing = User.query.filter_by(email="test@example.com").first()
        if existing:
            print("Cleaning up old test user...")
            db.session.delete(existing)
            db.session.commit()

    with app.test_client() as client:
        # 2. Simulate Registration Post
        print("Sending POST request to /auth/register...")
        reg_response = client.post('/auth/register', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        if b"Your account has been created!" not in reg_response.data:
            print("FAIL: Registration response does not contain success flash message.", file=sys.stderr)
            sys.exit(1)
        print("SUCCESS: Registration request returned success flash message.")
        
        # 3. Verify user exists in database
        with app.app_context():
            user = User.query.filter_by(email="test@example.com").first()
            if not user:
                print("FAIL: User was not found in the database.", file=sys.stderr)
                sys.exit(1)
            if user.name != "Test User":
                print(f"FAIL: User name is {user.name}, expected 'Test User'.", file=sys.stderr)
                sys.exit(1)
            if not user.check_password("password123"):
                print("FAIL: Password hash check failed.", file=sys.stderr)
                sys.exit(1)
            print("SUCCESS: User record successfully created and password hashed correctly in DB.")
            
        # 4. Simulate Login Post
        print("Sending POST request to /auth/login...")
        login_response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        if b"Welcome back, Test User!" not in login_response.data:
            print("FAIL: Login response does not contain welcome flash message.", file=sys.stderr)
            sys.exit(1)
        print("SUCCESS: Login request authenticated user and redirected correctly.")
        
        print("--- AUTHENTICATION MODULE FULLY FUNCTIONAL ---")
        sys.exit(0)

if __name__ == '__main__':
    verify_auth()

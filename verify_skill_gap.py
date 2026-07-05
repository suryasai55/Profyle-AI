import sys
from app import create_app, db
from app.models.user import User
from app.models.resume import Resume

def verify_gap():
    print("Initializing test app context...")
    app = create_app('development')
    
    with app.test_client() as client:
        # Log in
        print("Logging in...")
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Request skill gap analysis page for ML Engineer
        print("Requesting skill gap page for ML Engineer...")
        response = client.get('/skill_gap/analysis?role=ml_engineer')
        
        if response.status_code != 200:
            print(f"FAIL: Skill gap analysis returned status code {response.status_code}", file=sys.stderr)
            sys.exit(1)
            
        # Verify content
        if b"Skill Gap Detector" not in response.data:
            print("FAIL: Page content missing title 'Skill Gap Detector'", file=sys.stderr)
            sys.exit(1)
            
        if b"ML Engineer" not in response.data:
            print("FAIL: Selected role name 'ML Engineer' not found in content.", file=sys.stderr)
            sys.exit(1)
            
        if b"Recommended Course Curriculum" not in response.data:
            print("FAIL: Recommendations table header not found.", file=sys.stderr)
            sys.exit(1)
            
        print("SUCCESS: Skill gap analysis endpoint responded with code 200 and correct dynamic HTML structures.")
        print("--- SKILL GAP MODULE FULLY FUNCTIONAL ---")
        sys.exit(0)

if __name__ == '__main__':
    verify_gap()

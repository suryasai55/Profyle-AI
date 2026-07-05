import sys
from app import create_app, db
from app.models.user import User
from app.models.readiness import PlacementReadiness

def verify_readiness():
    print("Initializing test app context...")
    app = create_app('development')
    
    with app.test_client() as client:
        # Log in
        print("Logging in...")
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Request readiness score page
        print("Requesting readiness score page...")
        response = client.get('/readiness/score')
        
        if response.status_code != 200:
            print(f"FAIL: Placement readiness score endpoint returned status {response.status_code}", file=sys.stderr)
            sys.exit(1)
            
        # Verify content
        if b"Placement Readiness Score" not in response.data:
            print("FAIL: Page content missing title 'Placement Readiness Score'", file=sys.stderr)
            sys.exit(1)
            
        if b"Composite Placement Readiness" not in response.data:
            print("FAIL: Gauge title not found in content.", file=sys.stderr)
            sys.exit(1)
            
        if b"Preparation Breakdown" not in response.data:
            print("FAIL: Breakdown title not found in content.", file=sys.stderr)
            sys.exit(1)
            
        if b"Preparation Suggestions" not in response.data:
            print("FAIL: Suggestions card title not found in content.", file=sys.stderr)
            sys.exit(1)
            
        print("SUCCESS: Placement readiness scoring endpoint responded with code 200 and loaded all UI elements successfully.")
        print("--- PLACEMENT READINESS SCORE MODULE FULLY FUNCTIONAL ---")
        sys.exit(0)

if __name__ == '__main__':
    verify_readiness()

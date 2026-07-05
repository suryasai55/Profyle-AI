import sys
from app import create_app

def verify():
    print("Initializing Flask app factory...")
    try:
        app = create_app('development')
        print("Flask app factory initialized successfully!")
    except Exception as e:
        print(f"Error during app factory initialization: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("Simulating GET request to '/'...")
    try:
        with app.test_client() as client:
            response = client.get('/')
            print(f"Response Status Code: {response.status_code}")
            if response.status_code == 200:
                print("Homepage rendered successfully! HTML Content length:", len(response.data))
                print("--- VERIFICATION PASSED ---")
                sys.exit(0)
            else:
                print(f"Failed: Homepage returned status code {response.status_code}", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"Error during request simulation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    verify()

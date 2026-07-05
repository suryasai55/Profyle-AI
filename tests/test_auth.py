import unittest
from app import create_app, db
from app.models.user import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        """Set up testing app and clean database before each test."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean database and tear down context after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_model_password_hashing(self):
        """Test password hashing and verification helper methods."""
        user = User(name="Jane Doe", email="jane@example.com")
        user.set_password("mypassword")
        
        self.assertIsNotNone(user.password_hash)
        self.assertNotEqual(user.password_hash, "mypassword")
        self.assertTrue(user.check_password("mypassword"))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_user_registration_success(self):
        """Test successful registration of a unique user."""
        response = self.client.post('/auth/register', data={
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'password': 'safe_password_123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your account has been created!", response.data)
        
        # Verify database record
        user = User.query.filter_by(email="bob@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Bob Smith")

    def test_user_registration_duplicate_email(self):
        """Test registration fails when duplicate email is submitted."""
        # Create initial user
        user = User(name="Bob Smith", email="bob@example.com")
        user.set_password("initial")
        db.session.add(user)
        db.session.commit()
        
        # Try registering same email
        response = self.client.post('/auth/register', data={
            'name': 'Bob Other',
            'email': 'bob@example.com',
            'password': 'safe_password_123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Email address is already registered", response.data)

    def test_user_registration_missing_inputs(self):
        """Test registration fails when fields are omitted."""
        response = self.client.post('/auth/register', data={
            'name': '',
            'email': 'missing@example.com',
            'password': ''
        }, follow_redirects=True)
        
        self.assertIn(b"All fields are required.", response.data)

    def test_user_login_success(self):
        """Test authentication with correct credentials."""
        # Create user
        user = User(name="Alice Johnson", email="alice@example.com")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        
        response = self.client.post('/auth/login', data={
            'email': 'alice@example.com',
            'password': 'pass123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome back, Alice Johnson!", response.data)

    def test_user_login_wrong_credentials(self):
        """Test authentication fails with wrong credentials."""
        user = User(name="Alice Johnson", email="alice@example.com")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        
        response = self.client.post('/auth/login', data={
            'email': 'alice@example.com',
            'password': 'incorrect_password'
        }, follow_redirects=True)
        
        self.assertIn(b"Invalid email or password.", response.data)

if __name__ == '__main__':
    unittest.main()

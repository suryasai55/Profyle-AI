from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.user import User
from app.auth import auth

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Basic input validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        # Check if email already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address is already registered. Please login.', 'danger')
            return render_template('auth/register.html')

        try:
            # Create user
            new_user = User(name=name, email=email)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'danger')
            # Log the error
            from flask import current_app
            current_app.logger.error(f"Registration Error: {str(e)}")
            return render_template('auth/register.html')

    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate credentials and log in the user."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()
        
        # Verify credentials
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            
            # Handle next parameter for redirect after login
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    """Terminate the user session."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('dashboard.index'))

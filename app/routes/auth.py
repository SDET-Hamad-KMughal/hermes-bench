from flask import Blueprint, render_template, redirect, request, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User  # <-- Added the missing database model import

# Instantiate the authentication blueprint module
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Verify hashed database credentials and bind persistent user session instances."""
    if current_user.is_authenticated:
        return redirect('/')
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        
        # Query database record matching the provided unique email string
        user = User.query.filter_by(email=email).first()
        
        # Verify credentials using safe secure cryptographic hash comparison
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f"Welcome back, {user.username}! Session authenticated successfully.", "success")
            return redirect('/')
        else:
            flash("Invalid credentials match. Check email/password records and try again.", "danger")
            return redirect('/login')
            
    # Renders the actual login.html template file inside templates/auth/
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Process account registration payloads and build isolated user records."""
    if current_user.is_authenticated:
        return redirect('/')
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        
        # Identity Validation: Ensure records do not overlap existing test entries
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash("Error: Username or Email is already registered in the testbed system.", "danger")
            return redirect('/register')
            
        # Secure Hashing + Record State Ingestion
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            balance=100.0  # Assign standard credit balance pool for checkout testing
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! You can now log in with your credentials.", "success")
        return redirect('/login')
        
    # Renders the actual register.html template file inside templates/auth/
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Terminate the active session token and clear persistent authorization memory."""
    logout_user()
    flash("You have been cleanly logged out of the testbed environment.", "success")
    return redirect('/')
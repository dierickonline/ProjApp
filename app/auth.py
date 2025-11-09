from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.email import send_verification_email, generate_confirmation_token, confirm_token
from email_validator import validate_email, EmailNotValidError

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Validation
        errors = []

        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')

        if not email:
            errors.append('Email is required.')
        else:
            try:
                # Validate email format
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError as e:
                errors.append(f'Invalid email: {str(e)}')

        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')

        if password != password_confirm:
            errors.append('Passwords do not match.')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')

        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        user.verification_token = generate_confirmation_token(email)

        db.session.add(user)
        db.session.commit()

        # Send verification email
        verification_url = url_for('auth.verify_email', token=user.verification_token, _external=True)

        if send_verification_email(user, verification_url):
            flash('Registration successful! Please check your email to verify your account.', 'success')
        else:
            flash('Registration successful, but we could not send the verification email. Please contact support.', 'warning')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth.route('/verify/<token>')
def verify_email(token):
    """Verify email address"""
    email = confirm_token(token)

    if not email:
        flash('The verification link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))

    if user.is_verified:
        flash('Account already verified. Please log in.', 'info')
    else:
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        flash('Your email has been verified! You can now log in.', 'success')

    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return render_template('auth/login.html')

        if not user.is_verified:
            flash('Please verify your email address before logging in.', 'warning')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.username}!', 'success')

        # Redirect to next page if specified, otherwise to index
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    """Resend verification email"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()

        if user and not user.is_verified:
            user.verification_token = generate_confirmation_token(email)
            db.session.commit()

            verification_url = url_for('auth.verify_email', token=user.verification_token, _external=True)

            if send_verification_email(user, verification_url):
                flash('Verification email sent! Please check your inbox.', 'success')
            else:
                flash('Failed to send verification email. Please try again later.', 'danger')
        else:
            # Don't reveal if email exists or is already verified (security)
            flash('If that email is registered and unverified, a verification email has been sent.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('auth/resend_verification.html')

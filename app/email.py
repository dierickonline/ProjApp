from flask import render_template, current_app
from flask_mail import Message
from app import mail
from itsdangerous import URLSafeTimedSerializer
import secrets

def generate_verification_token():
    """Generate a unique verification token"""
    return secrets.token_urlsafe(32)

def get_serializer():
    """Get URL serializer for token generation"""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def generate_confirmation_token(email):
    """Generate a timed confirmation token"""
    serializer = get_serializer()
    return serializer.dumps(email, salt='email-confirm')

def confirm_token(token, expiration=3600):
    """Verify a confirmation token (default expiration: 1 hour)"""
    serializer = get_serializer()
    try:
        email = serializer.loads(
            token,
            salt='email-confirm',
            max_age=expiration
        )
        return email
    except:
        return False

def send_verification_email(user, verification_url):
    """Send verification email to user"""
    msg = Message(
        'Verify Your Email - Kanban Board',
        recipients=[user.email]
    )
    msg.body = f'''Hello {user.username},

Thank you for registering! Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 1 hour.

If you didn't create this account, please ignore this email.

Best regards,
Kanban Board Team
'''
    msg.html = render_template('emails/verify_email.html', user=user, verification_url=verification_url)

    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

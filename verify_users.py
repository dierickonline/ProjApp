"""
Script to manually verify users in the database
Run this if email verification is not working
"""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Get all unverified users
    unverified_users = User.query.filter_by(is_verified=False).all()

    if not unverified_users:
        print("No unverified users found.")
    else:
        print(f"Found {len(unverified_users)} unverified user(s):")
        for user in unverified_users:
            print(f"  - {user.username} ({user.email})")

        # Verify all users
        for user in unverified_users:
            user.is_verified = True
            user.verification_token = None

        db.session.commit()
        print("\nAll users have been verified!")

    # Show all users
    print("\nAll users in database:")
    all_users = User.query.all()
    for user in all_users:
        status = "✓ Verified" if user.is_verified else "✗ Not verified"
        print(f"  - {user.username} ({user.email}) - {status}")

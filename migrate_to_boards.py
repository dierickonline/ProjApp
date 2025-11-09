"""
Migration script to add Board model and update existing data
"""
from app import create_app, db
from app.models import Board, Lane

app = create_app()

with app.app_context():
    print("Starting migration to add boards support...")

    # Drop and recreate all tables (for development)
    print("Dropping existing tables...")
    db.drop_all()

    print("Creating new tables with Board model...")
    db.create_all()

    # Create a default board
    print("Creating default board...")
    default_board = Board(
        name='Main Project',
        description='Default Kanban board for your main project',
        color='#3B82F6'
    )
    db.session.add(default_board)
    db.session.commit()

    print(f"✓ Migration complete!")
    print(f"  - Created default board: '{default_board.name}' (ID: {default_board.id})")
    print(f"\nNOTE: All previous lanes and cards have been removed.")
    print(f"      Run 'python add_feature_cards.py' to restore the 29 feature cards.")
    print(f"      Or run 'flask --app run seed-db' to restore sample data.")

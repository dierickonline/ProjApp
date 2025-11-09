from app import create_app, db
from app.models import Board, Lane, Card, Category

app = create_app()

@app.cli.command()
def init_db():
    """Initialize the database with tables"""
    db.create_all()
    print("Database tables created successfully!")

@app.cli.command()
def seed_db():
    """Seed the database with sample data"""
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Create default board
    board = Board(
        name='Main Project',
        description='Default Kanban board for your main project',
        color='#3B82F6'
    )
    db.session.add(board)
    db.session.commit()

    # Create categories
    categories = [
        Category(name='Bug', color='#EF4444'),        # Red
        Category(name='Feature', color='#10B981'),    # Green
        Category(name='Enhancement', color='#3B82F6'), # Blue
        Category(name='Documentation', color='#8B5CF6'), # Purple
        Category(name='Urgent', color='#F59E0B')      # Orange
    ]

    for category in categories:
        db.session.add(category)

    db.session.commit()

    # Create lanes for the board
    lanes = [
        Lane(title='To Do', position=1.0, board_id=board.id),
        Lane(title='In Progress', position=2.0, board_id=board.id),
        Lane(title='Review', position=3.0, board_id=board.id),
        Lane(title='Done', position=4.0, board_id=board.id)
    ]

    for lane in lanes:
        db.session.add(lane)

    db.session.commit()

    # Create sample cards
    cards = [
        Card(
            title='Setup project repository',
            description='Initialize Git repository and create basic project structure',
            lane_id=lanes[3].id,  # Done
            position=1.0
        ),
        Card(
            title='Design database schema',
            description='Create ERD and define table relationships',
            lane_id=lanes[3].id,  # Done
            position=2.0
        ),
        Card(
            title='Implement user authentication',
            description='Add login and registration functionality',
            lane_id=lanes[1].id,  # In Progress
            position=1.0
        ),
        Card(
            title='Create API endpoints',
            description='Build RESTful API for CRUD operations',
            lane_id=lanes[1].id,  # In Progress
            position=2.0
        ),
        Card(
            title='Write unit tests',
            description='Add test coverage for core functionality',
            lane_id=lanes[2].id,  # Review
            position=1.0
        ),
        Card(
            title='Fix navigation bug',
            description='Resolve issue with broken links in mobile view',
            lane_id=lanes[0].id,  # To Do
            position=1.0
        ),
        Card(
            title='Update documentation',
            description='Add API documentation and usage examples',
            lane_id=lanes[0].id,  # To Do
            position=2.0
        ),
        Card(
            title='Optimize database queries',
            description='Improve performance for large datasets',
            lane_id=lanes[0].id,  # To Do
            position=3.0
        ),
    ]

    for card in cards:
        db.session.add(card)

    db.session.commit()

    # Assign categories to cards
    cards[0].categories = [categories[1]]  # Setup project - Feature
    cards[1].categories = [categories[1]]  # Design database - Feature
    cards[2].categories = [categories[1], categories[4]]  # User auth - Feature, Urgent
    cards[3].categories = [categories[2]]  # API endpoints - Enhancement
    cards[4].categories = [categories[2]]  # Unit tests - Enhancement
    cards[5].categories = [categories[0], categories[4]]  # Fix bug - Bug, Urgent
    cards[6].categories = [categories[3]]  # Documentation - Documentation
    cards[7].categories = [categories[2]]  # Optimize - Enhancement

    db.session.commit()

    print("Database seeded successfully!")
    print(f"Created 1 board: '{board.name}'")
    print(f"Created {len(categories)} categories")
    print(f"Created {len(lanes)} lanes")
    print(f"Created {len(cards)} cards")

if __name__ == '__main__':
    app.run(debug=True)

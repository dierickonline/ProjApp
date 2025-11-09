from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for many-to-many relationship between cards and categories
card_categories = db.Table('card_categories',
    db.Column('card_id', db.Integer, db.ForeignKey('cards.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with boards
    boards = db.relationship('Board', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat()
        }

class Board(db.Model):
    """Board containing lanes and cards for a project"""
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    color = db.Column(db.String(7), default='#3B82F6')  # Hex color code for theme
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship - cascade delete lanes when board is deleted
    lanes = db.relationship('Lane', backref='board', lazy=True,
                          cascade='all, delete-orphan', order_by='Lane.position')

    def to_dict(self):
        """Convert board to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at.isoformat(),
            'lane_count': len(self.lanes)
        }

class Lane(db.Model):
    """Lane (column) on the Kanban board"""
    __tablename__ = 'lanes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Float, nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship - cascade delete cards when lane is deleted
    cards = db.relationship('Card', backref='lane', lazy=True,
                          cascade='all, delete-orphan', order_by='Card.position')

    def to_dict(self):
        """Convert lane to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'position': self.position,
            'created_at': self.created_at.isoformat(),
            'card_count': len(self.cards)
        }

class Card(db.Model):
    """Card within a lane"""
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    lane_id = db.Column(db.Integer, db.ForeignKey('lanes.id'), nullable=False)
    position = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Many-to-many relationship with categories
    categories = db.relationship('Category', secondary=card_categories,
                                backref=db.backref('cards', lazy='dynamic'))

    def to_dict(self):
        """Convert card to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'lane_id': self.lane_id,
            'position': self.position,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'categories': [cat.to_dict() for cat in self.categories]
        }

class Category(db.Model):
    """Category/label for cards"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), nullable=False)  # Hex color code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert category to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color
        }

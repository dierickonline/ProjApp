from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Lane, Card, Category

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main Kanban board view"""
    lanes = Lane.query.order_by(Lane.position).all()
    categories = Category.query.all()
    return render_template('index.html', lanes=lanes, categories=categories)

# Lane routes
@bp.route('/lanes', methods=['POST'])
def create_lane():
    """Create a new lane"""
    title = request.form.get('title', '').strip()
    if not title:
        return 'Title is required', 400

    # Get the maximum position and add 1
    max_position = db.session.query(db.func.max(Lane.position)).scalar() or 0
    lane = Lane(title=title, position=max_position + 1)

    db.session.add(lane)
    db.session.commit()

    return render_template('partials/lane.html', lane=lane, categories=Category.query.all())

@bp.route('/lanes/<int:lane_id>', methods=['DELETE'])
def delete_lane(lane_id):
    """Delete a lane and all its cards"""
    lane = Lane.query.get_or_404(lane_id)
    db.session.delete(lane)
    db.session.commit()
    return '', 200

@bp.route('/lanes/reorder', methods=['PUT'])
def reorder_lanes():
    """Update lane positions after drag and drop"""
    lane_ids = request.json.get('lane_ids', [])

    for index, lane_id in enumerate(lane_ids):
        lane = Lane.query.get(lane_id)
        if lane:
            lane.position = index

    db.session.commit()
    return jsonify({'success': True})

# Card routes
@bp.route('/cards', methods=['POST'])
def create_card():
    """Create a new card"""
    title = request.form.get('title', '').strip()
    lane_id = request.form.get('lane_id', type=int)
    category_ids = request.form.getlist('category_ids', type=int)

    if not title or not lane_id:
        return 'Title and lane are required', 400

    lane = Lane.query.get_or_404(lane_id)

    # Get the maximum position in this lane and add 1
    max_position = db.session.query(db.func.max(Card.position)).filter_by(lane_id=lane_id).scalar() or 0

    card = Card(title=title, lane_id=lane_id, position=max_position + 1)

    # Add categories if provided
    if category_ids:
        categories = Category.query.filter(Category.id.in_(category_ids)).all()
        card.categories = categories

    db.session.add(card)
    db.session.commit()

    return render_template('partials/card.html', card=card)

@bp.route('/cards/<int:card_id>', methods=['GET'])
def get_card(card_id):
    """Get card details for modal"""
    card = Card.query.get_or_404(card_id)
    categories = Category.query.all()
    return render_template('partials/card_modal.html', card=card, all_categories=categories)

@bp.route('/cards/<int:card_id>/update', methods=['POST'])
def update_card(card_id):
    """Update card details"""
    card = Card.query.get_or_404(card_id)

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    category_ids = request.form.getlist('category_ids', type=int)

    # Debug logging
    print(f"DEBUG: Updating card {card_id}")
    print(f"DEBUG: Title: {title}")
    print(f"DEBUG: Description: {description}")
    print(f"DEBUG: Category IDs received: {category_ids}")
    print(f"DEBUG: Form data: {request.form}")

    if title:
        card.title = title
    if description is not None:
        card.description = description

    # Update categories - always process the category selection
    # category_ids will be a list (empty or with IDs)
    if category_ids:
        categories = Category.query.filter(Category.id.in_(category_ids)).all()
        print(f"DEBUG: Found categories: {[c.name for c in categories]}")
        card.categories = categories
    else:
        # Clear all categories if none selected
        print("DEBUG: Clearing all categories")
        card.categories = []

    db.session.commit()
    print(f"DEBUG: Card categories after commit: {[c.name for c in card.categories]}")

    return render_template('partials/card.html', card=card)

@bp.route('/cards/<int:card_id>', methods=['PUT'])
def move_card_put(card_id):
    """Update card via PUT (for backward compatibility with drag-drop)"""
    return move_card(card_id)

@bp.route('/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Delete a card"""
    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return '', 200

@bp.route('/cards/<int:card_id>/move', methods=['PUT'])
def move_card(card_id):
    """Move card to different lane or position"""
    card = Card.query.get_or_404(card_id)

    new_lane_id = request.json.get('lane_id', type=int)
    new_position = request.json.get('position', type=float)

    if new_lane_id:
        card.lane_id = new_lane_id
    if new_position is not None:
        card.position = new_position

    db.session.commit()
    return jsonify({'success': True})

@bp.route('/cards/reorder', methods=['PUT'])
def reorder_cards():
    """Reorder cards within a lane or across lanes"""
    updates = request.json.get('updates', [])

    for update in updates:
        card_id = update.get('card_id')
        lane_id = update.get('lane_id')
        position = update.get('position')

        card = Card.query.get(card_id)
        if card:
            if lane_id is not None:
                card.lane_id = lane_id
            if position is not None:
                card.position = position

    db.session.commit()
    return jsonify({'success': True})

# Category routes
@bp.route('/categories', methods=['POST'])
def create_category():
    """Create a new category"""
    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#3B82F6').strip()

    if not name:
        return 'Name is required', 400

    category = Category(name=name, color=color)
    db.session.add(category)
    db.session.commit()

    return jsonify(category.to_dict())

@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify([cat.to_dict() for cat in categories])

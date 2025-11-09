from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Board, Lane, Card, Category

bp = Blueprint('main', __name__)

def get_current_board():
    """Get the current board from session or return the first board owned by current user"""
    board_id = session.get('current_board_id')

    if board_id:
        board = Board.query.filter_by(id=board_id, user_id=current_user.id).first()
        if board:
            return board

    # If no board in session or board doesn't exist, get the first board for this user
    board = Board.query.filter_by(user_id=current_user.id).first()
    if board:
        session['current_board_id'] = board.id
    return board

@bp.route('/')
@login_required
def index():
    """Main Kanban board view"""
    current_board = get_current_board()

    if not current_board:
        # No boards exist, redirect to create one
        return render_template('index.html', lanes=[], categories=Category.query.all(),
                             boards=[], current_board=None)

    lanes = Lane.query.filter_by(board_id=current_board.id).order_by(Lane.position).all()
    categories = Category.query.all()
    # Only show boards owned by current user
    boards = Board.query.filter_by(user_id=current_user.id).all()

    return render_template('index.html', lanes=lanes, categories=categories,
                         boards=boards, current_board=current_board)

# Board routes
@bp.route('/boards', methods=['POST'])
@login_required
def create_board():
    """Create a new board"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    color = request.form.get('color', '#3B82F6').strip()

    if not name:
        return 'Name is required', 400

    board = Board(name=name, description=description, color=color, user_id=current_user.id)
    db.session.add(board)
    db.session.commit()

    # Switch to the new board
    session['current_board_id'] = board.id

    return redirect(url_for('main.index'))

@bp.route('/boards/<int:board_id>', methods=['GET'])
@login_required
def get_board(board_id):
    """Get board details"""
    board = Board.query.filter_by(id=board_id, user_id=current_user.id).first_or_404()
    return jsonify(board.to_dict())

@bp.route('/boards/<int:board_id>/update', methods=['POST'])
@login_required
def update_board(board_id):
    """Update board details"""
    board = Board.query.filter_by(id=board_id, user_id=current_user.id).first_or_404()

    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    color = request.form.get('color', '').strip()

    if name:
        board.name = name
    if description is not None:
        board.description = description
    if color:
        board.color = color

    db.session.commit()

    return redirect(url_for('main.index'))

@bp.route('/boards/<int:board_id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_board(board_id):
    """Delete a board and all its lanes/cards"""
    board = Board.query.filter_by(id=board_id, user_id=current_user.id).first_or_404()

    # Don't delete if it's the only board for this user
    if Board.query.filter_by(user_id=current_user.id).count() <= 1:
        return 'Cannot delete the only board', 400

    # If deleting the current board, switch to another one
    if session.get('current_board_id') == board_id:
        other_board = Board.query.filter(Board.id != board_id, Board.user_id == current_user.id).first()
        if other_board:
            session['current_board_id'] = other_board.id

    db.session.delete(board)
    db.session.commit()

    return redirect(url_for('main.index'))

@bp.route('/boards/<int:board_id>/switch', methods=['POST'])
@login_required
def switch_board(board_id):
    """Switch to a different board"""
    board = Board.query.filter_by(id=board_id, user_id=current_user.id).first_or_404()
    session['current_board_id'] = board.id
    return redirect(url_for('main.index'))

# Lane routes
@bp.route('/lanes', methods=['POST'])
@login_required
def create_lane():
    """Create a new lane"""
    current_board = get_current_board()
    if not current_board:
        return 'No board selected', 400

    title = request.form.get('title', '').strip()
    if not title:
        return 'Title is required', 400

    # Get the maximum position for this board and add 1
    max_position = db.session.query(db.func.max(Lane.position)).filter_by(
        board_id=current_board.id).scalar() or 0
    lane = Lane(title=title, position=max_position + 1, board_id=current_board.id)

    db.session.add(lane)
    db.session.commit()

    return redirect(url_for('main.index'))

@bp.route('/lanes/<int:lane_id>', methods=['DELETE'])
@login_required
def delete_lane(lane_id):
    """Delete a lane and all its cards"""
    lane = Lane.query.get_or_404(lane_id)
    # Verify the lane belongs to a board owned by current user
    if lane.board.user_id != current_user.id:
        return 'Unauthorized', 403
    db.session.delete(lane)
    db.session.commit()
    return '', 200

@bp.route('/lanes/reorder', methods=['PUT'])
@login_required
def reorder_lanes():
    """Update lane positions after drag and drop"""
    lane_ids = request.json.get('lane_ids', [])

    for index, lane_id in enumerate(lane_ids):
        lane = Lane.query.get(lane_id)
        if lane and lane.board.user_id == current_user.id:
            lane.position = index

    db.session.commit()
    return jsonify({'success': True})

# Card routes
@bp.route('/cards', methods=['POST'])
@login_required
def create_card():
    """Create a new card"""
    title = request.form.get('title', '').strip()
    lane_id = request.form.get('lane_id', type=int)
    category_ids = request.form.getlist('category_ids', type=int)

    if not title or not lane_id:
        return 'Title and lane are required', 400

    lane = Lane.query.get_or_404(lane_id)
    # Verify the lane belongs to a board owned by current user
    if lane.board.user_id != current_user.id:
        return 'Unauthorized', 403

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
@login_required
def get_card(card_id):
    """Get card details for modal"""
    card = Card.query.get_or_404(card_id)
    # Verify the card belongs to a board owned by current user
    if card.lane.board.user_id != current_user.id:
        return 'Unauthorized', 403
    categories = Category.query.all()
    return render_template('partials/card_modal.html', card=card, all_categories=categories)

@bp.route('/cards/<int:card_id>/update', methods=['POST'])
@login_required
def update_card(card_id):
    """Update card details"""
    card = Card.query.get_or_404(card_id)
    # Verify the card belongs to a board owned by current user
    if card.lane.board.user_id != current_user.id:
        return 'Unauthorized', 403

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    category_ids = request.form.getlist('category_ids', type=int)

    if title:
        card.title = title
    if description is not None:
        card.description = description

    # Update categories
    if category_ids:
        categories = Category.query.filter(Category.id.in_(category_ids)).all()
        card.categories = categories
    else:
        card.categories = []

    db.session.commit()

    return render_template('partials/card.html', card=card)

@bp.route('/cards/<int:card_id>', methods=['PUT'])
@login_required
def move_card_put(card_id):
    """Update card via PUT (for backward compatibility with drag-drop)"""
    return move_card(card_id)

@bp.route('/cards/<int:card_id>', methods=['DELETE'])
@login_required
def delete_card(card_id):
    """Delete a card"""
    card = Card.query.get_or_404(card_id)
    # Verify the card belongs to a board owned by current user
    if card.lane.board.user_id != current_user.id:
        return 'Unauthorized', 403
    db.session.delete(card)
    db.session.commit()
    return '', 200

@bp.route('/cards/<int:card_id>/move', methods=['PUT'])
@login_required
def move_card(card_id):
    """Move card to different lane or position"""
    card = Card.query.get_or_404(card_id)
    # Verify the card belongs to a board owned by current user
    if card.lane.board.user_id != current_user.id:
        return 'Unauthorized', 403

    new_lane_id = request.json.get('lane_id')
    new_position = request.json.get('position')

    if new_lane_id:
        card.lane_id = int(new_lane_id)
    if new_position is not None:
        card.position = float(new_position)

    db.session.commit()

    return jsonify({'success': True})

@bp.route('/cards/reorder', methods=['PUT'])
@login_required
def reorder_cards():
    """Reorder cards within a lane or across lanes"""
    updates = request.json.get('updates', [])

    for update in updates:
        card_id = update.get('card_id')
        lane_id = update.get('lane_id')
        position = update.get('position')

        card = Card.query.get(card_id)
        if card and card.lane.board.user_id == current_user.id:
            if lane_id is not None:
                card.lane_id = lane_id
            if position is not None:
                card.position = position

    db.session.commit()
    return jsonify({'success': True})

# Category routes
@bp.route('/categories', methods=['POST'])
@login_required
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
@login_required
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify([cat.to_dict() for cat in categories])

@bp.route('/categories/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    """Delete a category"""
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return '', 200

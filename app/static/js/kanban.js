// Global variables for SortableJS instances
let laneSortable = null;
let cardSortables = [];

// Initialize all drag and drop functionality
function initializeDragAndDrop() {
    initializeLaneDragDrop();
    initializeCardDragDrop();
}

// Initialize drag and drop for lanes
function initializeLaneDragDrop() {
    const board = document.getElementById('board');
    if (!board) return;

    // Destroy existing instance if it exists
    if (laneSortable) {
        laneSortable.destroy();
    }

    laneSortable = Sortable.create(board, {
        animation: 150,
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        dragClass: 'sortable-drag',
        handle: '.lane-header',
        onEnd: function(event) {
            // Get all lane IDs in the new order
            const lanes = board.querySelectorAll('.lane');
            const laneIds = Array.from(lanes).map(lane =>
                parseInt(lane.getAttribute('data-lane-id'))
            );

            // Send update to server
            fetch('/lanes/reorder', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ lane_ids: laneIds })
            })
            .catch(error => {
                console.error('Error reordering lanes:', error);
                alert('Failed to save lane order. Please refresh the page.');
            });
        }
    });
}

// Initialize drag and drop for cards
function initializeCardDragDrop() {
    const laneCards = document.querySelectorAll('.lane-cards');

    // Destroy existing instances
    cardSortables.forEach(sortable => sortable.destroy());
    cardSortables = [];

    laneCards.forEach(laneCardsContainer => {
        const sortable = Sortable.create(laneCardsContainer, {
            group: 'cards',  // Allow dragging between lanes
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            onEnd: function(event) {
                const cardId = parseInt(event.item.getAttribute('data-card-id'));
                const newLaneId = parseInt(event.to.getAttribute('data-lane-id'));
                const newPosition = event.newIndex;

                // Calculate position value
                const cards = event.to.querySelectorAll('.card');
                let positionValue;

                if (cards.length === 1) {
                    positionValue = 1.0;
                } else if (newPosition === 0) {
                    // Moving to the start
                    const nextCard = cards[1];
                    const nextPosition = parseFloat(nextCard.getAttribute('data-position') || (newPosition + 2));
                    positionValue = nextPosition / 2;
                } else if (newPosition === cards.length - 1) {
                    // Moving to the end
                    const prevCard = cards[newPosition - 1];
                    const prevPosition = parseFloat(prevCard.getAttribute('data-position') || newPosition);
                    positionValue = prevPosition + 1;
                } else {
                    // Moving between cards
                    const prevCard = cards[newPosition - 1];
                    const nextCard = cards[newPosition + 1];
                    const prevPosition = parseFloat(prevCard.getAttribute('data-position') || newPosition);
                    const nextPosition = parseFloat(nextCard.getAttribute('data-position') || (newPosition + 2));
                    positionValue = (prevPosition + nextPosition) / 2;
                }

                // Update card's data attribute
                event.item.setAttribute('data-position', positionValue);

                // Send update to server
                fetch(`/cards/${cardId}/move`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        lane_id: newLaneId,
                        position: positionValue
                    })
                })
                .catch(error => {
                    console.error('Error moving card:', error);
                    alert('Failed to save card position. Please refresh the page.');
                });
            }
        });

        cardSortables.push(sortable);
    });
}

// Card Modal Functions
function openCardModal(cardId) {
    const modal = document.getElementById('card-modal');
    const modalContent = document.getElementById('card-modal-content');

    // Fetch card details
    fetch(`/cards/${cardId}`)
        .then(response => response.text())
        .then(html => {
            modalContent.innerHTML = html;
            // Process HTMX attributes in the newly loaded content
            htmx.process(modalContent);
            modal.style.display = 'flex';
        })
        .catch(error => {
            console.error('Error loading card details:', error);
            alert('Failed to load card details.');
        });
}

function closeCardModal() {
    const modal = document.getElementById('card-modal');
    modal.style.display = 'none';
    return false; // Prevent default link behavior
}

// Category Modal Functions
function openCategoryModal() {
    const modal = document.getElementById('category-modal');
    loadCategories();
    modal.style.display = 'flex';
    return false; // Prevent default link behavior
}

function closeCategoryModal() {
    const modal = document.getElementById('category-modal');
    modal.style.display = 'none';
    return false;
}

function createCategory(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    fetch('/categories', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(category => {
        // Clear form
        form.reset();
        document.getElementById('category-color').value = '#3B82F6';

        // Reload categories list
        loadCategories();

        // Show success message
        alert('Category created successfully!');

        // Optionally reload the page to update category selects
        location.reload();
    })
    .catch(error => {
        console.error('Error creating category:', error);
        alert('Failed to create category.');
    });
}

function loadCategories() {
    fetch('/categories')
        .then(response => response.json())
        .then(categories => {
            const categoriesList = document.getElementById('categories-list');
            categoriesList.innerHTML = `
                <table style="width: 100%; border-collapse: collapse;">
                    ${categories.map(cat => `
                        <tr>
                            <td style="padding: 0.25rem 0;">
                                <span class="category-badge" style="background-color: ${cat.color};">${cat.name}</span>
                            </td>
                            <td style="width: 30px; text-align: right; padding: 0.25rem 0;">
                                <button type="button" class="delete-category-btn" onclick="deleteCategory(${cat.id})" style="background: none; color: #EF4444; border: none; padding: 0; cursor: pointer; font-size: 1.25rem; line-height: 1; font-weight: bold;">×</button>
                            </td>
                        </tr>
                    `).join('')}
                </table>
            `;
        })
        .catch(error => {
            console.error('Error loading categories:', error);
        });
}

function deleteCategory(categoryId) {
    if (!confirm('Are you sure you want to delete this category?')) {
        return;
    }

    fetch(`/categories/${categoryId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            // Reload categories list
            loadCategories();

            // Show success message
            alert('Category deleted successfully!');

            // Reload the page to update category selects in cards
            location.reload();
        } else {
            throw new Error('Failed to delete category');
        }
    })
    .catch(error => {
        console.error('Error deleting category:', error);
        alert('Failed to delete category.');
    });
}

// Lane Modal Functions
function openLaneModal() {
    const modal = document.getElementById('lane-modal');
    modal.style.display = 'flex';
    return false;
}

function closeLaneModal() {
    const modal = document.getElementById('lane-modal');
    modal.style.display = 'none';
    return false;
}

// Board Modal Functions
function openBoardModal() {
    const modal = document.getElementById('board-modal');
    modal.style.display = 'flex';
    return false;
}

function closeBoardModal() {
    const modal = document.getElementById('board-modal');
    modal.style.display = 'none';
    return false;
}

function switchBoard(boardId) {
    // Submit form to switch board
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/boards/${boardId}/switch`;
    document.body.appendChild(form);
    form.submit();
}

function switchToBoard(boardId) {
    // Alias for switchBoard (used in board management modal)
    switchBoard(boardId);
}

function editBoard(boardId) {
    // Hide display, show edit form
    document.getElementById(`board-display-${boardId}`).style.display = 'none';
    document.getElementById(`board-edit-${boardId}`).style.display = 'block';
}

function cancelEditBoard(boardId) {
    // Show display, hide edit form
    document.getElementById(`board-display-${boardId}`).style.display = 'block';
    document.getElementById(`board-edit-${boardId}`).style.display = 'none';
}

function saveBoard(boardId) {
    const name = document.getElementById(`board-name-${boardId}`).value.trim();
    const description = document.getElementById(`board-desc-${boardId}`).value.trim();

    if (!name) {
        alert('Board name is required');
        return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('description', description);

    fetch(`/boards/${boardId}/update`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            // Reload the page to show updated board
            location.reload();
        } else {
            throw new Error('Failed to update board');
        }
    })
    .catch(error => {
        console.error('Error updating board:', error);
        alert('Failed to update board.');
    });
}

function deleteBoard(boardId) {
    if (!confirm('Delete this board and all its lanes/cards?')) {
        return;
    }

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/boards/${boardId}/delete`;
    document.body.appendChild(form);
    form.submit();
}

// Close modals on backdrop click
document.addEventListener('click', function(event) {
    // Close modal if clicking on the overlay background (not the modal content)
    if (event.target.classList.contains('modal-overlay')) {
        event.target.style.display = 'none';
    }
});

// Close modals on ESC key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.style.display = 'none';
        });
    }
});

// Note: The delete button's inline onclick="event.stopPropagation()"
// prevents the card modal from opening when clicking delete.
// No additional event listener needed here.

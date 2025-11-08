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
            modal.showModal();
        })
        .catch(error => {
            console.error('Error loading card details:', error);
            alert('Failed to load card details.');
        });
}

function closeCardModal() {
    const modal = document.getElementById('card-modal');
    modal.close();
    return false; // Prevent default link behavior
}

// Category Modal Functions
function openCategoryModal() {
    const modal = document.getElementById('category-modal');
    loadCategories();
    modal.showModal();
    return false; // Prevent default link behavior
}

function closeCategoryModal() {
    const modal = document.getElementById('category-modal');
    modal.close();
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
            categoriesList.innerHTML = categories.map(cat => `
                <div class="category-item" style="margin-bottom: 0.5rem;">
                    <span class="category-badge" style="background-color: ${cat.color};">${cat.name}</span>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error loading categories:', error);
        });
}

// Lane Modal Functions
function openLaneModal() {
    const modal = document.getElementById('lane-modal');
    modal.showModal();
    return false; // Prevent default link behavior
}

function closeLaneModal() {
    const modal = document.getElementById('lane-modal');
    modal.close();
    return false;
}

function createLane(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    fetch('/lanes', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(html => {
        // Add the new lane to the board
        const board = document.getElementById('board');
        board.insertAdjacentHTML('beforeend', html);

        // Clear form
        form.reset();

        // Close modal
        closeLaneModal();

        // Reinitialize drag and drop
        initializeDragAndDrop();
    })
    .catch(error => {
        console.error('Error creating lane:', error);
        alert('Failed to create lane.');
    });
}

// Close modals on ESC key (native behavior for dialog element)
// Close modals on backdrop click
document.addEventListener('click', function(event) {
    const cardModal = document.getElementById('card-modal');
    const categoryModal = document.getElementById('category-modal');
    const laneModal = document.getElementById('lane-modal');

    if (event.target === cardModal) {
        closeCardModal();
    }
    if (event.target === categoryModal) {
        closeCategoryModal();
    }
    if (event.target === laneModal) {
        closeLaneModal();
    }
});

// Note: The delete button's inline onclick="event.stopPropagation()"
// prevents the card modal from opening when clicking delete.
// No additional event listener needed here.

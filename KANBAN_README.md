# Kanban Board - Python Web Application

A simple and elegant Kanban board web application built with Python Flask, featuring drag-and-drop functionality and a clean blue-themed interface. This is a lightweight alternative to Trello for personal task management.

## Features

- **Kanban Board Layout**: Organize tasks in customizable lanes (columns)
- **Drag & Drop**:
  - Reorder lanes by dragging
  - Move cards between lanes seamlessly
- **Card Management**:
  - Create, edit, and delete cards
  - Add title and description
  - Assign color-coded categories (labels)
  - View creation and modification dates
- **Lane Management**:
  - Create and delete lanes
  - Reorder lanes to match your workflow
- **Categories**: Create custom categories with colors for better organization
- **Clean UI**: Simple, minimalist design with various shades of blue

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTMX (dynamic interactions without JavaScript frameworks)
- **Drag & Drop**: SortableJS
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **ORM**: SQLAlchemy
- **CSS**: Pico CSS + Custom blue theme

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or navigate to the project directory**:
   ```bash
   cd ProjApp
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize and seed the database**:
   ```bash
   flask --app run seed-db
   ```
   This will create the database and populate it with sample lanes, cards, and categories.

6. **Run the application**:
   ```bash
   python run.py
   ```

7. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage

### Managing Lanes

- **Create a Lane**: Enter a title in the "Enter lane title..." input and click "+ Add Lane"
- **Delete a Lane**: Click the × button in the lane header (confirms before deleting)
- **Reorder Lanes**: Click and drag a lane by its header to reposition it

### Managing Cards

- **Create a Card**:
  - Enter a title in the "Add a card..." input within a lane
  - Optionally select categories from the dropdown
  - Click "+ Add"
- **View Card Details**: Click on any card to open the details modal
- **Edit a Card**: Click on a card, modify the details in the modal, and click "Save Changes"
- **Delete a Card**: Click the × button on the card (confirms before deleting)
- **Move a Card**: Click and drag a card to move it within a lane or to a different lane

### Managing Categories

- **Create a Category**:
  - Click "Manage Categories" in the top navigation
  - Enter a category name and choose a color
  - Click "Add Category"
- **View Categories**: All categories are displayed in the category management modal

## Project Structure

```
ProjApp/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # Database models (Lane, Card, Category)
│   ├── routes.py            # Application routes and API endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── custom.css   # Custom blue theme styles
│   │   └── js/
│   │       └── kanban.js    # Drag-and-drop and modal logic
│   └── templates/
│       ├── base.html        # Base template
│       ├── index.html       # Main board view
│       └── partials/        # Reusable HTML components
│           ├── lane.html
│           ├── card.html
│           └── card_modal.html
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── KANBAN_README.md        # This file
```

## Database Schema

### Tables

- **lanes**: Stores board columns
  - id, title, position, created_at, updated_at

- **cards**: Stores individual tasks
  - id, title, description, lane_id, position, created_at, updated_at

- **categories**: Stores category/label definitions
  - id, name, color, created_at

- **card_categories**: Many-to-many relationship between cards and categories
  - card_id, category_id

## Customization

### Changing the Color Scheme

Edit [app/static/css/custom.css](app/static/css/custom.css) and modify the CSS variables in the `:root` selector:

```css
:root {
    --primary: #3B82F6;        /* Primary blue color */
    --primary-hover: #2563EB;  /* Hover state */
    --lane-background: #E0E7FF; /* Lane background */
    /* ... other colors ... */
}
```

### Database Configuration

For production use with PostgreSQL:

1. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

2. Set the `DATABASE_URL` environment variable:
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost/kanban_db"
   ```

## Development

### Adding New Features

The application is structured to be easily extensible:

- **New routes**: Add to [app/routes.py](app/routes.py)
- **New models**: Add to [app/models.py](app/models.py)
- **New templates**: Add to `app/templates/` or `app/templates/partials/`
- **New styles**: Add to [app/static/css/custom.css](app/static/css/custom.css)

### Resetting the Database

To clear all data and start fresh:

```bash
flask --app run seed-db
```

This will drop all tables, recreate them, and add sample data.

## Future Enhancements

Potential features for future development:

- [ ] User authentication and multi-user support
- [ ] Board backgrounds and themes
- [ ] Card attachments and checklists
- [ ] Activity history and audit log
- [ ] Search and filter functionality
- [ ] Card archiving (soft delete)
- [ ] Keyboard shortcuts
- [ ] Export board to JSON/CSV
- [ ] Real-time collaboration with WebSockets

## License

This project is open source and available for personal and commercial use.

## Acknowledgments

- **Flask**: Lightweight Python web framework
- **HTMX**: Modern approach to building interactive web applications
- **SortableJS**: Drag-and-drop library
- **Pico CSS**: Minimal CSS framework

---

**Enjoy organizing your tasks with this simple Kanban board!**

# Quick Start Guide

## Get Started in 3 Minutes!

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
flask --app run seed-db
```

This creates the database with sample data:
- 4 lanes: To Do, In Progress, Review, Done
- 8 sample cards with various categories
- 5 pre-configured categories (Bug, Feature, Enhancement, Documentation, Urgent)

### 3. Run the Application

```bash
python run.py
```

Open your browser to: **http://127.0.0.1:5000**

## What You Can Do

- **Create lanes**: Add new columns to organize your workflow
- **Create cards**: Add tasks to any lane
- **Drag & Drop**: Move cards between lanes or reorder them
- **Add categories**: Label cards with colored categories
- **View details**: Click cards to see full details and edit them
- **Delete**: Remove lanes or cards you no longer need

## Folder Structure

```
ProjApp/
├── app/                     # Application code
│   ├── models.py           # Database models
│   ├── routes.py           # URL routes and logic
│   ├── templates/          # HTML templates
│   └── static/             # CSS and JavaScript
├── config.py               # Configuration
├── run.py                  # Start the app
└── requirements.txt        # Dependencies
```

## Troubleshooting

**Issue**: `ModuleNotFoundError`
- **Solution**: Make sure you activated the virtual environment and ran `pip install -r requirements.txt`

**Issue**: Database errors
- **Solution**: Run `flask --app run seed-db` to reset the database

**Issue**: Port already in use
- **Solution**: Change the port in [run.py](run.py): `app.run(debug=True, port=5001)`

## Next Steps

See [KANBAN_README.md](KANBAN_README.md) for complete documentation.

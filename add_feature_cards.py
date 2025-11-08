"""
Script to add 29 feature suggestion cards to the Kanban board
"""
from app import create_app, db
from app.models import Lane, Card, Category

app = create_app()

with app.app_context():
    # Find or create the Backlog/To Do lane
    backlog_lane = Lane.query.filter_by(title='To Do').first()

    if not backlog_lane:
        # If "To Do" doesn't exist, try "Backlog"
        backlog_lane = Lane.query.filter_by(title='Backlog').first()

    if not backlog_lane:
        # Create a Backlog lane if neither exists
        max_position = db.session.query(db.func.max(Lane.position)).scalar() or 0
        backlog_lane = Lane(title='Backlog', position=max_position + 1)
        db.session.add(backlog_lane)
        db.session.commit()
        print(f"Created 'Backlog' lane")

    # Get Enhancement category (or create if doesn't exist)
    enhancement_cat = Category.query.filter_by(name='Enhancement').first()
    if not enhancement_cat:
        enhancement_cat = Category(name='Enhancement', color='#3B82F6')
        db.session.add(enhancement_cat)
        db.session.commit()

    feature_cat = Category.query.filter_by(name='Feature').first()
    if not feature_cat:
        feature_cat = Category(name='Feature', color='#10B981')
        db.session.add(feature_cat)
        db.session.commit()

    # Get max position in the backlog lane
    max_position = db.session.query(db.func.max(Card.position)).filter_by(lane_id=backlog_lane.id).scalar() or 0

    # Define all 29 feature cards
    feature_cards = [
        # Quick Wins
        {
            'title': 'Due Dates for Cards',
            'description': '''Add a due_date field to cards with color coding:
- Red for overdue cards
- Yellow for cards due soon
- Filter and sort cards by due date

**Why**: Essential for task management, helps prioritize work
**Category**: Quick Win - Easy to implement, high impact''',
            'category': feature_cat
        },
        {
            'title': 'Card Archive (Instead of Delete)',
            'description': '''Implement soft-delete functionality:
- Add archived boolean field to cards
- Archive cards instead of permanently removing them
- "Show Archived" toggle to view/restore archived cards
- Archive button in card modal

**Why**: Safer than deletion, keeps history and allows recovery
**Category**: Quick Win - Easy to implement, high impact''',
            'category': enhancement_cat
        },
        {
            'title': 'Search Functionality',
            'description': '''Add search capability across the board:
- Search box in header
- Real-time search across card titles and descriptions
- Highlight matching cards
- Clear search button

**Why**: Essential as boards grow larger, quick access to specific cards
**Category**: Quick Win - Easy to implement, high impact''',
            'category': feature_cat
        },
        {
            'title': 'Filter by Category',
            'description': '''Enable filtering cards by category:
- Click category badge to filter all cards with that category
- "Clear filters" button
- Visual indicator when filter is active
- Combine multiple category filters

**Why**: Quick way to focus on specific work types (bugs, features, etc.)
**Category**: Quick Win - Easy to implement, high impact''',
            'category': enhancement_cat
        },
        {
            'title': 'Card Duplication',
            'description': '''Add ability to duplicate existing cards:
- "Duplicate" button in card modal
- Copies title, description, and categories
- Places duplicate in same lane
- Option to duplicate to different lane

**Why**: Saves time for repetitive tasks and similar work items
**Category**: Quick Win - Easy to implement, high impact''',
            'category': feature_cat
        },

        # Medium Effort, High Value
        {
            'title': 'Checklists within Cards',
            'description': '''Add sub-tasks/to-do lists to cards:
- Create checklist items within a card
- Check/uncheck items
- Show progress (e.g., "2/5 complete")
- Display progress bar on card face
- Delete checklist items

**Why**: Trello's most-used feature, breaks down complex tasks into manageable steps
**Category**: Medium Effort - High value feature''',
            'category': feature_cat
        },
        {
            'title': 'Card Comments/Activity Log',
            'description': '''Enable collaboration and tracking:
- Add comments to cards with timestamps
- Show activity timeline (created, moved, edited, commented)
- Display who made each change
- Sorted chronologically

**Why**: Enables collaboration and provides audit trail of changes
**Category**: Medium Effort - High value feature''',
            'category': feature_cat
        },
        {
            'title': 'User Assignment',
            'description': '''Add user authentication and card assignments:
- Simple user authentication system
- Assign cards to specific users
- Show user avatars/initials on cards
- Filter cards by assigned user
- "Assign to me" quick action

**Why**: Essential for team collaboration and accountability
**Category**: Medium Effort - High value feature''',
            'category': feature_cat
        },
        {
            'title': 'Priority Levels',
            'description': '''Add priority field to cards:
- Priority options: Low, Medium, High, Urgent
- Color-code card borders by priority
- Sort and filter by priority
- Visual indicators (icons or colors)

**Why**: Helps prioritize workload and identify critical tasks
**Category**: Medium Effort - High value feature''',
            'category': enhancement_cat
        },
        {
            'title': 'Card Cover Colors',
            'description': '''Add visual card customization:
- Optional colored header bar on cards
- Color picker for card covers
- Quick visual identification
- Complement category badges

**Why**: Visual organization, professional appearance, quick identification
**Category**: Medium Effort - High value feature''',
            'category': enhancement_cat
        },

        # Advanced Features
        {
            'title': 'Multiple Boards',
            'description': '''Support multiple project boards:
- Create different boards for different projects
- Board switcher/selector in header
- Each board has its own lanes/cards
- Board settings and configuration
- Default board selection

**Why**: Scale to multiple projects, separate work contexts
**Category**: Advanced Feature - More complex implementation''',
            'category': feature_cat
        },
        {
            'title': 'File Attachments',
            'description': '''Allow file uploads to cards:
- Upload files to cards
- Store files locally or use cloud storage
- Preview images inline
- Download attachments
- Show attachment count on card

**Why**: Central document repository, all resources in one place
**Category**: Advanced Feature - More complex implementation''',
            'category': feature_cat
        },
        {
            'title': 'Time Tracking',
            'description': '''Track time spent on tasks:
- Add estimated time and actual time fields
- Timer feature for active work
- Start/stop/pause timer
- Time reports per card/lane/board
- Time analytics dashboard

**Why**: Project management, billing, productivity tracking
**Category**: Advanced Feature - More complex implementation''',
            'category': feature_cat
        },
        {
            'title': 'Card Dependencies',
            'description': '''Manage relationships between cards:
- Link cards together (blocks/blocked by)
- Visual indicators for dependencies
- Prevent moving blocked cards
- Dependency graph visualization

**Why**: Manage complex workflows and task relationships
**Category**: Advanced Feature - More complex implementation''',
            'category': feature_cat
        },
        {
            'title': 'Board Templates',
            'description': '''Create reusable board structures:
- Save board layouts as templates
- Include lanes, sample cards, categories
- Quick start for common workflows
- Template library
- Import/export templates

**Why**: Speed up project setup, standardize processes
**Category**: Advanced Feature - More complex implementation''',
            'category': feature_cat
        },

        # UI/UX Enhancements
        {
            'title': 'Keyboard Shortcuts',
            'description': '''Add keyboard navigation:
- N: Create new card
- L: Create new lane
- /: Focus search
- Arrow keys: Navigate between cards
- Esc: Close modals
- E: Edit selected card

**Why**: Power users work faster, improved accessibility
**Category**: UI/UX Enhancement''',
            'category': enhancement_cat
        },
        {
            'title': 'Card Quick Edit',
            'description': '''Enable inline editing:
- Click card title to edit directly without modal
- Edit description inline
- Quick category assignment
- Faster workflow for simple changes

**Why**: Reduces clicks for simple edits, improved efficiency
**Category**: UI/UX Enhancement''',
            'category': enhancement_cat
        },
        {
            'title': 'Empty State Graphics',
            'description': '''Improve first-time user experience:
- Nice graphics when board/lane is empty
- Helpful tips for new users
- Onboarding guide
- Example board option

**Why**: Better first-time user experience, reduces confusion
**Category**: UI/UX Enhancement''',
            'category': enhancement_cat
        },
        {
            'title': 'Card Preview on Hover',
            'description': '''Quick information access:
- Show card description preview on hover
- Display categories and metadata
- Quick view without clicking
- Tooltip-style popup

**Why**: Faster information access, reduced clicks
**Category**: UI/UX Enhancement''',
            'category': enhancement_cat
        },

        # Analytics & Reporting
        {
            'title': 'Basic Analytics Dashboard',
            'description': '''Track board metrics:
- Cards per lane (distribution chart)
- Cards created over time (line graph)
- Completion rate (if using archive)
- Category distribution
- Time in each lane (average)

**Why**: Track productivity and progress, identify bottlenecks
**Category**: Analytics & Reporting''',
            'category': feature_cat
        },
        {
            'title': 'Export Board Data',
            'description': '''Data portability features:
- Export to JSON format
- Export to CSV (for spreadsheets)
- Export to PDF (for presentations)
- Backup functionality
- Import from exported files

**Why**: Data portability, backups, reporting, presentations
**Category**: Analytics & Reporting''',
            'category': feature_cat
        },
        {
            'title': 'Card Aging Indicator',
            'description': '''Identify stale work:
- Visual indicator for cards that haven\'t moved in X days
- Configurable age threshold
- Fade or highlight old cards
- Filter by card age

**Why**: Prevents forgotten tasks, identifies blockers
**Category**: Analytics & Reporting''',
            'category': enhancement_cat
        },

        # Notifications & Reminders
        {
            'title': 'Due Date Reminders',
            'description': '''Never miss deadlines:
- Browser notifications for upcoming due dates
- Email reminders (optional)
- Configurable reminder timing (1 day, 1 hour, etc.)
- Snooze functionality

**Why**: Never miss deadlines, proactive task management
**Category**: Notifications & Reminders''',
            'category': feature_cat
        },
        {
            'title': 'Activity Notifications',
            'description': '''Team awareness features:
- Notify when card is commented on
- Notify when card is moved
- Notify when assigned to card
- Configurable notification preferences

**Why**: Team awareness, real-time collaboration
**Category**: Notifications & Reminders''',
            'category': feature_cat
        },

        # Fun/Polish Features
        {
            'title': 'Dark Mode',
            'description': '''Theme customization:
- Toggle between light and dark themes
- Automatic theme based on system preference
- Custom blue theme for dark mode
- Theme persistence across sessions

**Why**: User preference, reduces eye strain, modern UX
**Category**: Polish & Fun''',
            'category': enhancement_cat
        },
        {
            'title': 'Board Backgrounds',
            'description': '''Visual customization:
- Custom colors for board background
- Background images/patterns
- Gradient options
- Per-board customization

**Why**: Personalization, visual appeal, brand customization
**Category**: Polish & Fun''',
            'category': enhancement_cat
        },
        {
            'title': 'Confetti Animation',
            'description': '''Celebrate achievements:
- Confetti animation when card moves to "Done" lane
- Optional sound effects
- Configurable completion lane
- Toggle on/off in settings

**Why**: Gamification, positive feedback, motivation
**Category**: Polish & Fun''',
            'category': enhancement_cat
        },
        {
            'title': 'Card Emojis',
            'description': '''Visual fun and categorization:
- Add emoji picker for card titles
- Emoji reactions on cards
- Emoji in lane titles
- Quick emoji shortcuts

**Why**: Visual fun, quick categorization, modern UX
**Category**: Polish & Fun''',
            'category': enhancement_cat
        },
        {
            'title': 'WIP Limits for Lanes',
            'description': '''Enforce workflow limits:
- Set work-in-progress limits per lane
- Visual warning when limit exceeded
- Block adding cards when at limit (optional)
- WIP limit indicator on lane header

**Why**: Kanban best practice, prevents overload, improves flow
**Category**: Advanced Feature - Kanban methodology''',
            'category': feature_cat
        }
    ]

    # Create all cards
    created_count = 0
    for idx, card_data in enumerate(feature_cards):
        card = Card(
            title=card_data['title'],
            description=card_data['description'],
            lane_id=backlog_lane.id,
            position=max_position + idx + 1
        )

        # Add category
        if card_data.get('category'):
            card.categories = [card_data['category']]

        db.session.add(card)
        created_count += 1

    db.session.commit()

    print(f"✓ Successfully created {created_count} feature cards in '{backlog_lane.title}' lane!")
    print(f"  Refresh your browser to see the new cards.")

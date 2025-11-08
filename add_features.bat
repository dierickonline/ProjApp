@echo off
echo ====================================
echo Adding Feature Cards to Kanban Board
echo ====================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Running script to add 29 feature cards...
python add_feature_cards.py

echo.
echo ====================================
echo Done! Refresh your browser to see the new cards.
echo ====================================
pause

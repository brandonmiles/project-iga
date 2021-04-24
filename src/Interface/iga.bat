@ECHO OFF
ECHO "Starting IGA Web Application..."
set FLASK_APP=app.py
set FLASK_ENV=development
flask run

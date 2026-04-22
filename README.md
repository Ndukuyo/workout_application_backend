# workout_application_backend

## Description
A workout app for personal trainers to manage workouts and exercises. Track exercises in workouts with reps/sets or duration metrics. Built with Flask, SQLAlchemy, and Marshmallow.

## Tech Stack
- Python 3.9+
- Flask
- SQLAlchemy
- Marshmallow
- SQLite

## Setup and Running instructions
1. Install dependencies
pipenv install flask flask-sqlalchemy flask-migrate marshmallow marshmallow-sqlalchemy sqlalchemy
pipenv shell

2. Setup Database
   - While in the app folder:
   - flask db init
   - flask dm migrate -m "message"
   - flask db upgrade

3 Seed the database
python seed.py

4 Run application
To run :
- Move into the app folder:
   cd app
- Run program:  
   python app.py
  
5 End points
- To List all workouts (method => GET) http://localhost:5555/workouts
- To create workout (method => POST) http://localhost:5555/workouts
- To delete workout (method => DELETE)  http://localhost:5555/workouts/<id>
- To crete exercise (method => POST) http://localhost:5555/exercises 
- TO list all exercises (method => GET) http://localhost:5555/exercises
- To delete exercise (method => DELETE) http://localhost:5555/exercises/<id> 



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

**Method	         Endpoint                  	                           Description**
-GET	            /workouts	                                          List all workouts
-GET	            /workouts/<id>	                                       Get workout with exercises
-POST	            /workouts	                                          Create workout
-DELETE           /workouts/<id>	                                       Delete workout
-GET	            /exercises	                                          List all exercises
-GET	            /exercises/<id>	                                    Get exercise with workouts
-POST	            /exercises	                                          Create exercise
-DELETE	         /exercises/<id>	                                    Delete exercise
-POST	            /workouts/<id>/exercises/<id>/workout_exercises      	Add exercise to workout



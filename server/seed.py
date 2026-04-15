#!/usr/bin/env python3

from app import app
from models import db, Exercise, Workout, WorkoutExercise
from datetime import date, timedelta
import random

def seed_database():
    with app.app_context():
        print("Clearing existing data...")
    
        db.session.query(WorkoutExercise).delete()
        db.session.query(Workout).delete()
        db.session.query(Exercise).delete()
        db.session.commit()
        
        print("Creating exercises...")
        exercises = [
            Exercise(name="Bench Press", category="strength", equipment_needed=True),
            Exercise(name="Squats", category="strength", equipment_needed=False),
            Exercise(name="Deadlifts", category="strength", equipment_needed=True),
            Exercise(name="Pull-ups", category="strength", equipment_needed=False),
            Exercise(name="Running", category="cardio", equipment_needed=False),
            Exercise(name="Cycling", category="cardio", equipment_needed=True),
            Exercise(name="Yoga", category="flexibility", equipment_needed=False),
            Exercise(name="Plank", category="strength", equipment_needed=False),
            Exercise(name="Jumping Jacks", category="cardio", equipment_needed=False),
            Exercise(name="Lunges", category="strength", equipment_needed=False),
        ]
        
        db.session.add_all(exercises)
        db.session.commit()
        print(f"Created {len(exercises)} exercises")
        
        print("Creating workouts...")
        workouts = [
            Workout(date=date.today() - timedelta(days=2), duration_minutes=45, notes="Upper body focus"),
            Workout(date=date.today() - timedelta(days=1), duration_minutes=60, notes="Leg day - feeling strong"),
            Workout(date=date.today(), duration_minutes=30, notes="Quick cardio session"),
            Workout(date=date.today() + timedelta(days=1), duration_minutes=75, notes="Full body workout"),
            Workout(date=date.today() + timedelta(days=3), duration_minutes=50, notes="HIIT training"),
        ]
        
        db.session.add_all(workouts)
        db.session.commit()
        print(f"Created {len(workouts)} workouts")
        
        print("Creating workout exercises...")
        workout_exercises = [
            
            WorkoutExercise(workout_id=1, exercise_id=1, reps=10, sets=3),  
            WorkoutExercise(workout_id=1, exercise_id=4, reps=8, sets=3),   
            WorkoutExercise(workout_id=1, exercise_id=7, duration_seconds=60), 
            
        
            WorkoutExercise(workout_id=2, exercise_id=2, reps=12, sets=4), 
            WorkoutExercise(workout_id=2, exercise_id=3, reps=8, sets=3),   
            WorkoutExercise(workout_id=2, exercise_id=10, reps=15, sets=3), 
            
            
            WorkoutExercise(workout_id=3, exercise_id=5, duration_seconds=1200),
            WorkoutExercise(workout_id=3, exercise_id=6, duration_seconds=900),  
            WorkoutExercise(workout_id=3, exercise_id=9, reps=50, sets=3),      
            
        
            WorkoutExercise(workout_id=4, exercise_id=1, reps=10, sets=3), 
            WorkoutExercise(workout_id=4, exercise_id=2, reps=15, sets=3),  
            WorkoutExercise(workout_id=4, exercise_id=5, duration_seconds=600), 
            WorkoutExercise(workout_id=4, exercise_id=8, duration_seconds=90),  
            
        
            WorkoutExercise(workout_id=5, exercise_id=9, reps=30, sets=5),  
            WorkoutExercise(workout_id=5, exercise_id=5, duration_seconds=300), 
            WorkoutExercise(workout_id=5, exercise_id=8, duration_seconds=60),  
        ]
        
        db.session.add_all(workout_exercises)
        db.session.commit()
        print(f"Created {len(workout_exercises)} workout exercises")
        
        print("Database seeded successfully!")
        
        
        print("\n === Database Summary ===")
        print(f"Exercises: {Exercise.query.count()}")
        print(f"Workouts: {Workout.query.count()}")
        print(f"WorkoutExercises: {WorkoutExercise.query.count()}")
        
        
        print("\n === Testing Validations ===")
        
        
        print("\n Testing Exercise validations...")
        try:
            bad_exercise = Exercise(name="A", category="invalid")
            db.session.add(bad_exercise)
            db.session.commit()
        except (ValueError, Exception) as e:
            print(f" Validation caught bad exercise: {str(e)}")
            db.session.rollback()
        
        
        print("\n Testing Workout validations...")
        try:
            bad_workout = Workout(date="2023-13-45", duration_minutes=-10)
            db.session.add(bad_workout)
            db.session.commit()
        except (ValueError, Exception) as e:
            print(f" Validation caught bad workout: {str(e)}")
            db.session.rollback()
        
        
        print("\n Testing WorkoutExercise validations...")
        try:
            bad_we = WorkoutExercise(workout_id=1, exercise_id=1)
            bad_we.validate_complete()
        except ValueError as e:
            print(f" Validation caught missing metrics: {str(e)}")
        
        try:
            bad_we = WorkoutExercise(workout_id=1, exercise_id=1, reps=10, sets=3, duration_seconds=60)
            bad_we.validate_complete()
        except ValueError as e:
            print(f" Validation caught both metrics types: {str(e)}")

if __name__ == '__main__':
    seed_database()
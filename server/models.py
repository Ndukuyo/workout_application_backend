from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint
from datetime import datetime

db = SQLAlchemy()

class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, default=False)

    workout_exercises = db.relationship('WorkoutExercise', backref='exercise', cascade='all, delete-orphan')

    
    __table_args__ = (
        CheckConstraint('length(name) >= 2', name='check_exercise_name_length'),
        CheckConstraint("category IN ('strength', 'cardio', 'flexibility', 'balance', 'endurance')", 
        name='check_exercise_category_valid'),
    )
    

    @validates('name')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Exercise name cannot be empty")
        if len(name.strip()) < 2:
            raise ValueError("Exercise name must be at least 2 characters long")
        if len(name.strip()) > 100:
            raise ValueError("Exercise name must be less than 100 characters")
        return name.strip()
    
    @validates('category')
    def validate_category(self, key, category):
        valid_categories = ['strength', 'cardio', 'flexibility', 'balance', 'endurance']
        if not category:
            raise ValueError("Category cannot be empty")
        if category.lower() not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return category.lower()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'equipment_needed': self.equipment_needed
        }




class Workout(db.Model):
    __tablename__ = 'workouts'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    workout_exercises = db.relationship('WorkoutExercise', backref='workout', cascade='all, delete-orphan')

       
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='check_duration_positive'),
        CheckConstraint('duration_minutes <= 480', name='check_duration_max'), 
    )
    
    
    @validates('duration_minutes')
    def validate_duration(self, key, duration):
        if duration is None:
            raise ValueError("Duration cannot be empty")
        if duration <= 0:
            raise ValueError("Duration must be greater than 0 minutes")
        if duration > 480:
            raise ValueError("Duration cannot exceed 480 minutes (8 hours)")
        return duration
    
    @validates('date')
    def validate_date(self, key, date):
        if date is None:
            raise ValueError("Date cannot be empty")
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return date
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'duration_minutes': self.duration_minutes,
            'notes': self.notes
        }


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

        
   
    __table_args__ = (
        CheckConstraint('(reps IS NOT NULL AND sets IS NOT NULL AND duration_seconds IS NULL) OR '
        '(reps IS NULL AND sets IS NULL AND duration_seconds IS NOT NULL) OR '
        '(reps IS NULL AND sets IS NULL AND duration_seconds IS NULL)', 
        name='check_exercise_metrics'),
        CheckConstraint('reps IS NULL OR reps > 0', name='check_reps_positive'),
        CheckConstraint('sets IS NULL OR sets > 0', name='check_sets_positive'),
        CheckConstraint('duration_seconds IS NULL OR duration_seconds > 0', name='check_duration_positive'),
    )
    
  
    @validates('reps', 'sets', 'duration_seconds')
    def validate_metrics(self, key, value):
      
        return value
    
    def validate_complete(self):
       
        has_reps_sets = self.reps is not None and self.sets is not None
        has_duration = self.duration_seconds is not None
        
        if not has_reps_sets and not has_duration:
            raise ValueError("Either (reps and sets) or duration_seconds must be provided")
        
        if has_reps_sets and has_duration:
            raise ValueError("Cannot provide both (reps/sets) and duration_seconds")
        
        if has_reps_sets:
            if self.reps <= 0:
                raise ValueError("Reps must be greater than 0")
            if self.sets <= 0:
                raise ValueError("Sets must be greater than 0")
        
        if has_duration and self.duration_seconds <= 0:
            raise ValueError("Duration seconds must be greater than 0")
        
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'workout_id': self.workout_id,
            'exercise_id': self.exercise_id,
            'reps': self.reps,
            'sets': self.sets,
            'duration_seconds': self.duration_seconds
        }
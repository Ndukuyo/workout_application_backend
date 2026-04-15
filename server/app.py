from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from marshmallow import Schema, fields, validate, ValidationError, pre_load
from models import db, Exercise, Workout, WorkoutExercise
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

def validate_reps_sets_duration(data):

    has_reps_sets = data.get('reps') is not None and data.get('sets') is not None
    has_duration = data.get('duration_seconds') is not None
    
    if not has_reps_sets and not has_duration:
        raise ValidationError("Either (reps and sets) or duration_seconds must be provided")
    
    if has_reps_sets and has_duration:
        raise ValidationError("Cannot provide both (reps/sets) and duration_seconds")
    
    return data

class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=[
        validate.Length(min=2, max=100, error="Exercise name must be between 2 and 100 characters")
    ])
    category = fields.Str(required=True, validate=[
        validate.OneOf(['strength', 'cardio', 'flexibility', 'balance', 'endurance'],
                      error="Category must be one of: strength, cardio, flexibility, balance, endurance")
    ])
    equipment_needed = fields.Bool(dump_default=False)
    
    @pre_load
    def validate_name_not_empty(self, data, **kwargs):
        if 'name' in data and data['name']:
            data['name'] = data['name'].strip()
            if not data['name']:
                raise ValidationError({'name': 'Exercise name cannot be empty or only whitespace'})
        return data

class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True, format='%Y-%m-%d')
    duration_minutes = fields.Int(required=True, validate=[
        validate.Range(min=1, max=480, error="Duration must be between 1 and 480 minutes")
    ])
    notes = fields.Str(dump_default=None, allow_none=True)
    
    @pre_load
    def validate_date_format(self, data, **kwargs):
        if 'date' in data and data['date']:
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(data['date'])):
                raise ValidationError({'date': 'Date must be in YYYY-MM-DD format'})
        return data

class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
    reps = fields.Int(validate=validate.Range(min=1), allow_none=True)
    sets = fields.Int(validate=validate.Range(min=1), allow_none=True)
    duration_seconds = fields.Int(validate=validate.Range(min=1), allow_none=True)
    
    @pre_load
    def validate_metrics_combination(self, data, **kwargs):
        return validate_reps_sets_duration(data)
    
    @pre_load
    def validate_positive_values(self, data, **kwargs):
        if data.get('reps') is not None and data.get('reps') <= 0:
            raise ValidationError({'reps': 'Reps must be greater than 0'})
        if data.get('sets') is not None and data.get('sets') <= 0:
            raise ValidationError({'sets': 'Sets must be greater than 0'})
        if data.get('duration_seconds') is not None and data.get('duration_seconds') <= 0:
            raise ValidationError({'duration_seconds': 'Duration seconds must be greater than 0'})
        return data


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()



@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return make_response(jsonify({'errors': error.messages}), 400)

@app.errorhandler(ValueError)
def handle_value_error(error):
    return make_response(jsonify({'error': str(error)}), 400)

@app.errorhandler(404)
def handle_not_found(error):
    return make_response(jsonify({'error': 'Resource not found'}), 404)


@app.route('/workouts', methods=['GET'])
def get_workouts():
  
    workouts = Workout.query.all()
    result = workouts_schema.dump(workouts)
    return make_response(jsonify(result), 200)

@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
   
    workout = Workout.query.get(id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)
    
  
    workout_data = workout_schema.dump(workout)
    exercises_data = []
    
    for we in workout.workout_exercises:
        exercise_info = we.exercise.to_dict()
        exercise_info['workout_exercise_details'] = {
            'reps': we.reps,
            'sets': we.sets,
            'duration_seconds': we.duration_seconds,
            'workout_exercise_id': we.id
        }
        exercises_data.append(exercise_info)
    
    workout_data['exercises'] = exercises_data
    return make_response(jsonify(workout_data), 200)

@app.route('/workouts', methods=['POST'])
def create_workout():
   
    try:
        data = request.get_json()
        validated_data = workout_schema.load(data)
        
        workout = Workout(
            date=validated_data['date'],
            duration_minutes=validated_data['duration_minutes'],
            notes=validated_data.get('notes')
        )
        
        db.session.add(workout)
        db.session.commit()
        
        result = workout_schema.dump(workout)
        return make_response(jsonify(result), 201)
    
    except ValidationError as e:
        return make_response(jsonify({'errors': e.messages}), 400)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
 
    workout = Workout.query.get(id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)
    
    db.session.delete(workout)
    db.session.commit()
    
    return make_response(jsonify({'message': 'Workout successfully deleted'}), 200)


@app.route('/exercises', methods=['GET'])
def get_exercises():

    exercises = Exercise.query.all()
    result = exercises_schema.dump(exercises)
    return make_response(jsonify(result), 200)

@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
   
    exercise = Exercise.query.get(id)
    if not exercise:
        return make_response(jsonify({'error': 'Exercise not found'}), 404)

    exercise_data = exercise_schema.dump(exercise)
    workouts_data = []
    
    for we in exercise.workout_exercises:
        workout_info = we.workout.to_dict()
        workout_info['workout_exercise_details'] = {
            'reps': we.reps,
            'sets': we.sets,
            'duration_seconds': we.duration_seconds
        }
        workouts_data.append(workout_info)
    
    exercise_data['workouts'] = workouts_data
    return make_response(jsonify(exercise_data), 200)

@app.route('/exercises', methods=['POST'])
def create_exercise():
    
    try:
        data = request.get_json()
        validated_data = exercise_schema.load(data)
        
        exercise = Exercise(
            name=validated_data['name'],
            category=validated_data['category'],
            equipment_needed=validated_data.get('equipment_needed', False)
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        result = exercise_schema.dump(exercise)
        return make_response(jsonify(result), 201)
    
    except ValidationError as e:
        return make_response(jsonify({'errors': e.messages}), 400)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)

@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
  
    exercise = Exercise.query.get(id)
    if not exercise:
        return make_response(jsonify({'error': 'Exercise not found'}), 404)
    
    db.session.delete(exercise)
    db.session.commit()
    
    return make_response(jsonify({'message': 'Exercise successfully deleted'}), 200)



@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):

    try:
      
        workout = Workout.query.get(workout_id)
        if not workout:
            return make_response(jsonify({'error': 'Workout not found'}), 404)
        
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return make_response(jsonify({'error': 'Exercise not found'}), 404)
        
        data = request.get_json()
        data['workout_id'] = workout_id
        data['exercise_id'] = exercise_id
        
  
        validated_data = workout_exercise_schema.load(data)
        
   
        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=validated_data.get('reps'),
            sets=validated_data.get('sets'),
            duration_seconds=validated_data.get('duration_seconds')
        )
        
     
        workout_exercise.validate_complete()
        
        db.session.add(workout_exercise)
        db.session.commit()
        
        result = workout_exercise_schema.dump(workout_exercise)
        return make_response(jsonify(result), 201)
    
    except ValidationError as e:
        return make_response(jsonify({'errors': e.messages}), 400)
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
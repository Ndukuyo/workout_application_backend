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
    equipment_needed = fields.Bool(missing=False)
    
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
    notes = fields.Str(missing=None, allow_none=True)
    
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

    pass

@app.route('/workouts', methods=['GET'])
def get_workouts():

    pass

@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):

    pass

@app.route('/workouts', methods=['POST'])
def create_workout():
  
    pass

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):

    pass



@app.route('/exercises', methods=['GET'])
def get_exercises():

    pass

@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):

    pass

@app.route('/exercises', methods=['POST'])
def create_exercise():

    pass

@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):

    pass



@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):

    pass

if __name__ == '__main__':
    app.run(port=5555, debug=True)
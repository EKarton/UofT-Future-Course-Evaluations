
# ML libraries
from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
from tensorflow import keras

import numpy as np

# Database libraries
import sys
sys.path.append('../Database')
from instructors_table import InstructorsTable

# Web app libraries
from flask import Flask, request, redirect, url_for, flash, jsonify, render_template
from flask_cors import CORS, cross_origin
import pickle as p
import json
import base64

import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

model = None
input_encoder = None
output_scaler = None
instructors_table = None

def make_prediction(course_code, instructor):
    new_input = np.array([[course_code, instructor]])
    new_input = input_encoder.transform(new_input)
    new_input = new_input.toarray()

    prediction = model.predict(new_input)
    return output_scaler.inverse_transform(prediction)

def has_instructor_from_course(course_code, abbrev_instructor_name):
    sql = """SELECT DISTINCT instructors.full_instructor_name
             FROM instructors JOIN evaluations ON instructors.instructor_id = evaluations.instructor_id
             WHERE evaluations.course_id = (
                 SELECT course_id
                 FROM courses
                 WHERE courses.course_code = %s
             )
             AND instructors.abbrev_instructor_name = %s; """

    results = instructors_table.execute_sql(sql, (course_code, abbrev_instructor_name))

    if len(results) > 0:
        return results[0][0]
    return None

def has_instructor_from_dept(dept, abbrev_instructor_name):
    sql = """SELECT DISTINCT instructors.full_instructor_name
             FROM instructors JOIN evaluations ON instructors.instructor_id = evaluations.instructor_id
             WHERE evaluations.dept_id = (
                SELECT dept_id
                FROM depts
                WHERE depts.dept_code = %s
             )
             AND instructors.abbrev_instructor_name = %s; """

    results = instructors_table.execute_sql(sql, (dept, abbrev_instructor_name))

    if len(results) > 0:
        return results[0][0]
    return None

def has_instructor(abbrev_instructor_name):
    sql = """SELECT DISTINCT instructors.full_instructor_name
             FROM instructors 
             WHERE instructors.abbrev_instructor_name = %s; """

    results = instructors_table.execute_sql(sql, (abbrev_instructor_name, ))

    if len(results) > 0:
        return results[0][0]
    return None

def get_fullname_from_abbreviation(course_code, abbrev_instructor_name):

    if course_code is not None:
        dept = course_code[0:3]

        instructor = has_instructor_from_course(course_code, abbrev_instructor_name)
        if instructor is not None:
            return instructor

        instructor = has_instructor_from_dept(dept, abbrev_instructor_name)
        if instructor is not None:
            return instructor

    instructor = has_instructor(abbrev_instructor_name)
    if instructor is not None:
        return instructor

    return None

def get_past_course_ratings_by_course_code(course_code):
    sql = """SELECT full_instructor_name, term, year, cat_1, cat_2, cat_3, cat_4, cat_5, cat_6, cat_7, cat_8 
             FROM evaluations 
             JOIN instructors ON evaluations.instructor_id = instructors.instructor_id 
             JOIN sessions ON evaluations.session_id = sessions.session_id
             WHERE course_id = (
                SELECT course_id
                FROM courses 
                WHERE course_code like %s
             ); """

    results = instructors_table.execute_sql(sql, (course_code, ))
    parsed_results = []
    for result in results:
        parsed_results.append({
            "instructor": result[0],
            "term": result[1],
            "year": result[2],
            "ratings": result[3 : 11]
        })
    
    return parsed_results

def get_course_ratings_by_instructor(instructor_name):
    sql = """SELECT course_code, term, year, cat_1, cat_2, cat_3, cat_4, cat_5, cat_6, cat_7, cat_8 
             FROM evaluations 
             JOIN sessions ON evaluations.session_id = sessions.session_id 
             JOIN courses ON evaluations.course_id = courses.course_id 
             WHERE instructor_id = (
                SELECT instructor_id 
                FROM instructors 
                WHERE instructors.full_instructor_name = %s
            ); """

    results = instructors_table.execute_sql(sql, (instructor_name, ))
    parsed_results = []
    for result in results:
        parsed_results.append({
            "course_code": result[0],
            "term": result[1],
            "year": result[2],
            "ratings": result[3 : 11]
        })
    
    return parsed_results

def get_course_ratings_by_course_code_and_instructor(course_code, instructor_name):
    sql = """SELECT term, year, cat_1, cat_2, cat_3, cat_4, cat_5, cat_6, cat_7, cat_8 
             FROM evaluations 
             JOIN sessions ON evaluations.session_id = sessions.session_id 
             WHERE instructor_id = (
                 SELECT instructor_id 
                 FROM instructors 
                 WHERE instructors.full_instructor_name = %s
             ) 
             AND course_id = (
                 SELECT course_id 
                 FROM courses 
                 WHERE courses.course_code = %s
             ); """

    results = instructors_table.execute_sql(sql, (instructor_name, course_code))
    parsed_results = []
    for result in results:
        parsed_results.append({
            "term": result[0],
            "year": result[1],
            "ratings": result[2 : 10]
        })
    
    return parsed_results

@app.route('/api/v1/evals/past', methods=['GET'])
# @cross_origin(origins="*", methods=['GET'])
def get_past_evals():
    course_code = None
    instructor = None

    if 'course_code' in request.args:
        course_code = request.args.get('course_code')

    if 'instructor' in request.args:
        instructor = request.args.get('instructor')

    elif 'abbrev_instructor' in request.args:
        abbrev_instructor = request.args.get('abbrev_instructor')
        instructor = get_fullname_from_abbreviation(course_code, abbrev_instructor)

        if instructor is None:
            return 'Abbreviated name ' + abbrev_instructor + ' cannot be known', 400

    print(course_code, instructor)

    if course_code is None and instructor is None:
        return 'Must have at least \'course_code\', \'instructor\', or \'abbrev_instructor\' in request query', 400

    elif course_code is None:
        return jsonify(get_course_ratings_by_instructor(instructor)), 200

    elif instructor is None:
        return jsonify(get_past_course_ratings_by_course_code(course_code)), 200

    else:
        return jsonify(get_course_ratings_by_course_code_and_instructor(course_code, instructor)), 200

@app.route('/api/evals/future', methods=['GET'])
# @cross_origin(origins="*", methods=['GET'])
def get_future_evals():
    course = request.args.get('course')
    instructor = None
    
    if 'instructor' in request.args:
        instructor = request.args.get('instructor')

    elif 'abbrev_instructor' in request.args:
        abbrev_instructor = request.args.get('abbrev_instructor')
        instructor = get_fullname_from_abbreviation(course, abbrev_instructor)

        if instructor is None:
            return 'Abbreviated name ' + abbrev_instructor + ' cannot be known', 400

    else:
        return 'Must have \'instructor\' or \'abbrev_instructor\' in query string', 400

    if course is None:
        return 'Must include \'courses\' in the query string', 400
    
    if instructor is None:
        return 'Instructor ' + instructor + ' must be known', 400

    try:
        ratings = make_prediction(course, instructor)[0].tolist()
        return jsonify(ratings), 200
    except Exception as e:
        print("Exception raised:", e, file=sys.stderr)
        return 'Rating with course ' + course + ' with instructor ' + instructor + ' cannot be determined', 400

def handle_bulk_request(courses, instructors, abbrev_instructors):
    results = []
    for i in range(len(courses)):
        course = courses[i]
        instructor = None
        instructor_name_in_response = None

        if instructors is not None:
            instructor = instructors[i]
            instructor_name_in_response = instructors[i]
        else:
            instructor = get_fullname_from_abbreviation(course, abbrev_instructors[i])
            instructor_name_in_response = abbrev_instructors[i]

        result = None
        try:
            ratings = make_prediction(course, instructor)[0].tolist()
            result = {
                'course': course,
                'instructor': instructor_name_in_response,
                'status': 'ok',
                'ratings': ratings
            }

        except Exception as e:
            print("Exception raised:", e, file=sys.stderr)
            result = {
                'course': course,
                'instructor': instructor_name_in_response,
                'status': 'fail',
                'error': 'Rating with course ' + str(course) + ' with instructor ' + str(instructor_name_in_response) + ' cannot be determined'
            }
        finally:
            results.append(result)

    return jsonify(results), 200

@app.route('/api/v2/bulk/evals/future', methods=['POST'])
# @cross_origin(origins="*", methods=['POST'])
def post_future_evals_in_bulk():
    courses = None
    instructors = None
    abbrev_instructors = None

    json_object = request.get_json()
    if json_object is not None:

        if 'courses' in json_object:
            courses = json_object['courses']

        if 'instructors' in json_object:
            instructors = json_object['instructors']

        if 'abbrev_instructors' in json_object:
            abbrev_instructors = json_object['abbrev_instructors']

    if courses is None:
        return 'Must include \'courses\' in the JSON body', 400
    
    if instructors is None and abbrev_instructors is None:
        return 'Must include either \'instructor\' or \'abbrev_instructors\' in JSON body', 400

    if instructors is not None and len(courses) != len(instructors):
        return 'Number of courses and instructors must be the same', 400
    
    if abbrev_instructors is not None and len(courses) != len(abbrev_instructors):
        return 'Number of courses and instructors must be the same', 400

    return handle_bulk_request(courses, instructors, abbrev_instructors)

@app.route('/api/bulk/evals/future', methods=['GET'])
# @cross_origin(origins="*", methods=['GET'])
def get_future_evals_in_bulk():
    courses = None
    instructors = None
    abbrev_instructors = None

    if 'courses' in request.args:
        courses = request.args.get('courses').split(',')

    if 'instructors' in request.args:
        instructors = request.args.get('instructors').split(',')

    elif 'abbrev_instructors' in request.args:
        abbrev_instructors = request.args.get('abbrev_instructors').split(',')

    if courses is None:
        return 'Must include \'courses\' in the query string', 400
    
    if instructors is None and abbrev_instructors is None:
        return 'Must include either \'instructor\' or \'abbrev_instructors\' in query string', 400

    if instructors is not None and len(courses) != len(instructors):
        return 'Number of courses and instructors must be the same', 400
    
    if abbrev_instructors is not None and len(courses) != len(abbrev_instructors):
        return 'Number of courses and instructors must be the same', 400

    return handle_bulk_request(courses, instructors, abbrev_instructors)

@app.route('/api/status', methods=['GET'])
# @cross_origin(origins="*", methods=['GET'])
def get_status():
    return 'OK', 200

@app.route('/evals/future', methods=['GET'])
# @cross_origin(origins="*", methods=['GET'])
def get_future_evals_page():
    return render_template('future-evals.html')

def load_app_prerequisites():
    global model, input_encoder, output_scaler, instructors_table

    # Load credentials from the .env file
    load_dotenv()

    # Load the DB
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    app_port = os.getenv("APP_PORT")

    # See if it is a debugger
    is_debugging_on = os.getenv("ENABLE_APP_DEBUGGER") == 'True'
    
    instructors_table = InstructorsTable(host, port, db_name, user, password)
    instructors_table.start()

    # Load the ML model
    modelfile = '../ML Model/saved-model.h5'
    model = keras.models.load_model(modelfile)

    input_encoder_file = '../ML Model/saved-input-encoder.pkl'
    input_encoder = p.load(open(input_encoder_file, 'rb'))

    output_scaler_file = '../ML Model/saved-output-scalar.pkl'
    output_scaler = p.load(open(output_scaler_file, 'rb'))

if __name__ == '__main__':
    load_app_prerequisites()
    app.run(debug=is_debugging_on, host='0.0.0.0', port=app_port)


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
from flask import Flask, request, redirect, url_for, flash, jsonify
import pickle as p
import json

import os
from dotenv import load_dotenv

app = Flask(__name__)
model = None
input_encoder = None
output_scaler = None
instructors_table = None

def make_prediction(course_code, instructor):
    new_input = np.array([[course_code, instructor]])
    new_input = input_encoder.transform(new_input)

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

@app.route('/api/evals/future', methods=['GET'])
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
        return 'Course ' + course + ' must be known', 400
    
    if instructor is None:
        return 'Instructor ' + instructor + ' must be known', 400

    try:
        ratings = make_prediction(course, instructor)[0].tolist()
        return jsonify(ratings), 200
    except:
        return 'Rating with course ' + course + ' with instructor ' + instructor + ' cannot be determined', 400

@app.route('/api/bulk/evals/future', methods=['GET'])
def get_future_evalsin_bulk():
    courses = request.args.get('courses').split(',')
    instructors = []

    if 'instructors' in request.args:
        instructors = request.args.get('instructors').split(',')

        if len(courses) != len(instructors):
            return "Number of courses does not equal to the number of instructors", 400

    elif 'abbrev_instructors' in request.args:
        abbrev_instructors = request.args.get('abbrev_instructors').split(',')

        if len(courses) != len(abbrev_instructors):
            return "Number of courses does not equal to the number of instructors", 400

        for i in range(len(abbrev_instructors)):
            course_code = courses[i]

            fullname = get_fullname_from_abbreviation(course_code, abbrev_instructors[i])
            instructors.append(fullname)

    results = []

    for i in range(len(courses)):
        course = courses[i]
        instructor = instructors[i]
        ratings = make_prediction(course, instructor)[0].tolist()

        result = {
            'course': course,
            'instructor': instructor,
            'future-ratings': {
                'cat1': ratings[0],
                'cat2': ratings[1],
                'cat3': ratings[2],
                'cat4': ratings[3],
                'cat5': ratings[4],
                'cat6': ratings[5],
                'cat7': ratings[6],
                'cat8': ratings[7],
                'cat9': ratings[8]
            },

            # If the course was taught before, show the ratings of all ratings with that course
            # Else show the rating of all courses taught by this instructor
            'past-ratings': {

            }
        }

        results.append(result)

    return jsonify(results)

if __name__ == '__main__':
    # Load credentials from the .env file
    load_dotenv()

    # Load the DB
    host = os.getenv("HOST")
    db_name = os.getenv("DATABASE_NAME")
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    instructors_table = InstructorsTable(host, db_name, user, password)
    instructors_table.start()

    # Load the ML model
    modelfile = '../ML Model/saved-model.h5'
    model = keras.models.load_model(modelfile)

    input_encoder_file = '../ML Model/saved-input-encoder.pkl'
    input_encoder = p.load(open(input_encoder_file, 'rb'))

    output_scaler_file = '../ML Model/saved-output-scalar.pkl'
    output_scaler = p.load(open(output_scaler_file, 'rb'))

    app.run(debug=True, host='0.0.0.0')

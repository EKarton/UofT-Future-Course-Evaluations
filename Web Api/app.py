from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
from tensorflow import keras

import numpy as np

from flask import Flask, request, redirect, url_for, flash, jsonify
import pickle as p
import json

app = Flask(__name__)
model = None
input_encoder = None
output_scaler = None

def make_prediction(course_code, instructor):
    new_input = np.array([[course_code, instructor]])
    new_input = input_encoder.transform(new_input)

    prediction = model.predict(new_input)
    return output_scaler.inverse_transform(prediction)

'''
    New problem: Given CSC324H1 and Liu, D. it should output the ratings for CSC324H1 and David Liu.
    Idea: Make a table for "David Liu" to "Liu, D". 
'''
def get_fullname_from_abbreviation(course_code, lastname, firstname_abbrev):
    pass

@app.route('/api/evals', methods=['GET'])
def get_future_evals():
    courses = request.args.get('courses').split(',')
    instructors = request.args.get('instructors').split(',')

    first_name_abbrev_instructors = request.args.get('abbrev_first_name_instructors').split(',')
    last_name_instructors = request.args.get('last_name_instructors').split(',')

    if len(first_name_abbrev_instructors) > 0:
        for i in range(len(last_name_instructors)):
            course_code = courses[i]
            lastname = last_name_instructors[i]
            firstname_abbrev = first_name_abbrev_instructors[i]

            fullname = get_fullname_from_abbreviation(course_code, lastname, firstname_abbrev)
            instructors.append(fullname)

    print(courses)
    print(instructors)

    results = []

    for i in range(len(courses)):
        course = courses[i]
        instructor = instructors[i]
        ratings = make_prediction(course, instructor)[0].tolist()

        print(ratings)

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
    modelfile = 'saved-model.h5'
    model = keras.models.load_model(modelfile)

    input_encoder_file = 'saved-input-encoder.pkl'
    input_encoder = p.load(open(input_encoder_file, 'rb'))

    output_scaler_file = 'saved-output-scalar.pkl'
    output_scaler = p.load(open(output_scaler_file, 'rb'))

    app.run(debug=True, host='0.0.0.0')

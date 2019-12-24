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

@app.route('/api/evals', methods=['GET'])
def get_evals():
    courses = request.args.get('courses').split(',')
    instructors = request.args.get('instructors').split(',')
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
